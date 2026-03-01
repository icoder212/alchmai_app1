"""Sentiment analysis analyzer"""
from typing import Dict, List
from transformers import pipeline
import torch

from .base import BaseAnalyzer
from src.data.alpha_vantage import alpha_vantage_client
from src.data.finnhub_client import finnhub_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer(BaseAnalyzer):
    """Analyzes news and social sentiment"""
    
    def __init__(self):
        super().__init__()
        self.finbert = None
        self._load_model()
    
    def _load_model(self):
        """Load FinBERT model (lazy loading)"""
        try:
            self.logger.info("Loading FinBERT model...")
            self.finbert = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("FinBERT model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load FinBERT model: {e}. Using fallback.")
            self.finbert = None
    
    def analyze(self, symbol: str, **kwargs) -> Dict:
        """
        Perform sentiment analysis
        
        Args:
            symbol: Trading symbol
            **kwargs: Additional parameters
            
        Returns:
            Dict with recommendation, score, reasoning
        """
        self.logger.info(f"Starting sentiment analysis for {symbol}")
        
        try:
            # Get recent news
            news = self._get_recent_news(symbol, hours=24)
            
            if not news:
                return self._neutral_response("No recent news available")
            
            # Analyze sentiment of each article
            sentiments = self._analyze_sentiments(news)

            if not sentiments:
                return self._neutral_response("Could not analyze news sentiment")

            # Count positive vs negative news
            positive_count = len([s for s in sentiments if s['score'] > 0])
            negative_count = len([s for s in sentiments if s['score'] < 0])
            neutral_count = len([s for s in sentiments if s['score'] == 0])
            total_count = len(sentiments)

            # Use count ratio as the primary signal — this is robust across both
            # Alpha Vantage scores (small: ±0.05–0.20) and FinBERT scores (large:
            # ±0.60–0.99).  Averaging raw scores across mixed sources collapses to
            # near-zero even when 66% of articles are positive.
            #
            # ratio = (positive - negative) / total  →  -1.0 … +1.0
            # score = 50 + ratio × 50                →  0 … 100
            #
            # Examples:
            #   33 pos / 17 neg / 50 total  → ratio = +0.32 → score = 66   (BUY)
            #   10 pos / 40 neg / 50 total  → ratio = -0.60 → score = 20   (SELL)
            #   25 pos / 25 neg / 50 total  → ratio =  0.00 → score = 50   (NEUTRAL)
            ratio = (positive_count - negative_count) / total_count  # -1 to +1
            score_from_ratio = 50.0 + (ratio * 50.0)

            # Determine recommendation
            if ratio > 0.05:   # >52.5 % positive → BUY
                recommendation = "BUY"
                score = min(100.0, score_from_ratio)
            elif ratio < -0.05:  # <47.5 % positive → SELL
                recommendation = "SELL"
                score = max(0.0, score_from_ratio)
            else:
                recommendation = "NEUTRAL"
                score = 50.0

            # Use the same score-based confidence formula as all other analyzers
            confidence = self._calculate_confidence(score)
            
            reasoning = (
                f"{positive_count} positive, {negative_count} negative, "
                f"{neutral_count} neutral news in last 24h "
                f"(sentiment ratio: {ratio:+.2f})"
            )
            
            self.logger.info(
                f"Sentiment analysis complete: {recommendation} "
                f"(score: {score:.1f}, confidence: {confidence:.1f}%)"
            )
            
            return {
                "recommendation": recommendation,
                "score": score,
                "reasoning": reasoning,
                "confidence": confidence,
                "sentiment_ratio": round(ratio, 3),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count
            }
        except Exception as e:
            self.logger.error(f"Sentiment analysis error for {symbol}: {e}")
            return self._neutral_response(f"Error in sentiment analysis: {str(e)}")
    
    def _get_recent_news(self, symbol: str, hours: int = 24) -> List[Dict]:
        """Get recent news articles"""
        news = []
        
        # Try Alpha Vantage News Sentiment API
        try:
            av_news = alpha_vantage_client.get_news_sentiment(symbol, limit=50)
            for article in av_news:
                # Prefer the ticker-specific sentiment score (more accurate) over the
                # article-wide overall_sentiment_score.  Alpha Vantage includes a
                # ticker_sentiment[] array; we look for our symbol inside it.
                ticker_score = None
                for ts in article.get("ticker_sentiment", []):
                    if ts.get("ticker", "").upper() == symbol.upper():
                        ticker_score = float(ts.get("ticker_sentiment_score", 0))
                        break
                # Fall back to overall score only when the ticker isn't listed
                sentiment_score = (
                    ticker_score
                    if ticker_score is not None
                    else article.get("overall_sentiment_score", 0)
                )
                news.append({
                    "title": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "published": article.get("time_published", ""),
                    "sentiment_score": sentiment_score
                })
        except Exception as e:
            self.logger.warning(f"Alpha Vantage news failed: {e}")
        
        # Try Finnhub news
        try:
            fh_news = finnhub_client.get_company_news(symbol, days=1)
            for article in fh_news:
                news.append({
                    "title": article.get("headline", ""),
                    "summary": article.get("summary", ""),
                    "published": article.get("datetime", ""),
                    "sentiment_score": None  # Will analyze with FinBERT
                })
        except Exception as e:
            self.logger.warning(f"Finnhub news failed: {e}")
        
        return news[:50]  # Limit to 50 articles
    
    def _build_text_for_analysis(self, article: Dict) -> str:
        """
        Build the text to feed to FinBERT.
        Combine title + summary for richer signal, truncated to 512 chars
        (FinBERT's token limit maps roughly to 512 characters).
        """
        title = (article.get("title") or "").strip()
        summary = (article.get("summary") or "").strip()

        if title and summary:
            combined = f"{title}. {summary}"
        else:
            combined = title or summary

        # FinBERT max input is 512 tokens; 512 chars is a safe character limit
        return combined[:512]

    def _analyze_sentiments(self, news: List[Dict]) -> List[Dict]:
        """Analyze sentiment of news articles"""
        sentiments = []

        for article in news:
            text = self._build_text_for_analysis(article)
            if not text:
                continue

            # If Alpha Vantage already provided a sentiment score, use it
            if article.get("sentiment_score") is not None:
                score = float(article.get("sentiment_score", 0))
                sentiments.append({
                    "headline": text,
                    "sentiment": "positive" if score > 0 else "negative" if score < 0 else "neutral",
                    "score": score,
                    "published": article.get("published", "")
                })
                continue

            # Use FinBERT on combined title + summary
            if self.finbert:
                try:
                    result = self.finbert(text)[0]

                    # Convert to score (-1 to +1)
                    if result['label'] == 'positive':
                        score = result['score']
                    elif result['label'] == 'negative':
                        score = -result['score']
                    else:  # neutral
                        score = 0

                    sentiments.append({
                        "headline": text,
                        "sentiment": result['label'],
                        "score": score,
                        "published": article.get("published", "")
                    })
                except Exception as e:
                    self.logger.warning(f"FinBERT analysis error: {e}")
            else:
                # Fallback: simple keyword-based sentiment
                score = self._simple_sentiment(text)
                sentiments.append({
                    "headline": text,
                    "sentiment": "positive" if score > 0 else "negative" if score < 0 else "neutral",
                    "score": score,
                    "published": article.get("published", "")
                })

        return sentiments
    
    def _simple_sentiment(self, text: str) -> float:
        """Simple keyword-based sentiment (fallback)"""
        positive_words = ["beat", "surge", "rally", "gain", "rise", "up", "strong", "bullish"]
        negative_words = ["fall", "drop", "plunge", "crash", "down", "weak", "bearish", "miss"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 0.3
        elif negative_count > positive_count:
            return -0.3
        else:
            return 0.0
    
    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response"""
        return {
            "recommendation": "NEUTRAL",
            "score": 50.0,
            "reasoning": reason,
            "confidence": 0.0
        }
