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
            
            # Calculate aggregate sentiment
            avg_sentiment = sum(s['score'] for s in sentiments) / len(sentiments)
            
            # Determine recommendation
            if avg_sentiment > 0.2:
                recommendation = "BUY"
                score = min(100, 50 + (avg_sentiment * 100))
            elif avg_sentiment < -0.2:
                recommendation = "SELL"
                score = max(0, 50 + (avg_sentiment * 100))
            else:
                recommendation = "NEUTRAL"
                score = 50.0
            
            confidence = min(100, abs(avg_sentiment) * 100)
            
            # Count positive vs negative news
            positive_count = len([s for s in sentiments if s['score'] > 0])
            negative_count = len([s for s in sentiments if s['score'] < 0])
            neutral_count = len([s for s in sentiments if s['score'] == 0])
            
            reasoning = (
                f"{positive_count} positive, {negative_count} negative, "
                f"{neutral_count} neutral news in last 24h "
                f"(avg sentiment: {avg_sentiment:.3f})"
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
                "avg_sentiment": round(avg_sentiment, 3),
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
                news.append({
                    "title": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "published": article.get("time_published", ""),
                    "sentiment_score": article.get("overall_sentiment_score", 0)
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
    
    def _analyze_sentiments(self, news: List[Dict]) -> List[Dict]:
        """Analyze sentiment of news articles"""
        sentiments = []
        
        for article in news:
            headline = article.get("title", "") or article.get("summary", "")
            if not headline:
                continue
            
            # If Alpha Vantage already provided sentiment, use it
            if article.get("sentiment_score") is not None:
                score = float(article.get("sentiment_score", 0))
                # Convert from -1 to +1 scale
                sentiments.append({
                    "headline": headline,
                    "sentiment": "positive" if score > 0 else "negative" if score < 0 else "neutral",
                    "score": score,
                    "published": article.get("published", "")
                })
                continue
            
            # Otherwise, use FinBERT
            if self.finbert:
                try:
                    result = self.finbert(headline)[0]
                    
                    # Convert to score (-1 to +1)
                    if result['label'] == 'positive':
                        score = result['score']
                    elif result['label'] == 'negative':
                        score = -result['score']
                    else:  # neutral
                        score = 0
                    
                    sentiments.append({
                        "headline": headline,
                        "sentiment": result['label'],
                        "score": score,
                        "published": article.get("published", "")
                    })
                except Exception as e:
                    self.logger.warning(f"FinBERT analysis error: {e}")
            else:
                # Fallback: simple keyword-based sentiment
                score = self._simple_sentiment(headline)
                sentiments.append({
                    "headline": headline,
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
