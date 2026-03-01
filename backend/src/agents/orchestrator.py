"""CrewAI orchestrator for multi-agent trading signal generation"""
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
from datetime import datetime

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from src.config import settings
from src.models.signal import TradingSignal
from src.processors.input_processor import InputProcessor
from src.analyzers.fundamental import FundamentalAnalyzer
from src.analyzers.economic import EconomicAnalyzer
from src.analyzers.technical import TechnicalAnalyzer
from src.analyzers.sentiment import SentimentAnalyzer
from src.synthesis.decision_synthesis import DecisionSynthesizer
from src.validators.safety_validator import SafetyValidator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TradingSignalOrchestrator:
    """Orchestrates the 4 analysis agents using CrewAI"""
    
    def __init__(self):
        """Initialize orchestrator with LLM and agents"""
        if not settings.openai_api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Please set OPENAI_API_KEY in your .env file."
            )
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            api_key=settings.openai_api_key
        )
        
        self.input_processor = InputProcessor()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.economic_analyzer = EconomicAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.decision_synthesizer = DecisionSynthesizer()
        self.safety_validator = SafetyValidator()
        
        self.agents = self._create_agents()
        logger.info("TradingSignalOrchestrator initialized")
    
    def _create_agents(self) -> Dict:
        """Create all 4 CrewAI analysis agents"""
        
        # 1. Fundamental Agent
        fundamental_agent = Agent(
            role='Fundamental Analyst',
            goal='Analyze company financials and fundamentals to determine investment value',
            backstory='''You are an expert fundamental analyst with 20 years of experience 
            analyzing company financial statements, earnings reports, and business fundamentals. 
            You specialize in identifying undervalued and overvalued stocks based on financial metrics.''',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 2. Economic Agent
        economic_agent = Agent(
            role='Economic Analyst',
            goal='Analyze macroeconomic conditions and their impact on asset prices',
            backstory='''You are a seasoned economist who tracks GDP, inflation, unemployment, 
            central bank policies, and their impact on financial markets. You understand how 
            macroeconomic trends affect different asset classes.''',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 3. Technical Agent
        technical_agent = Agent(
            role='Technical Analyst',
            goal='Analyze 15-minute charts and technical indicators for short-term trading signals',
            backstory='''You are a professional technical analyst specializing in short-term 
            trading signals using RSI, MACD, moving averages, and chart patterns. You excel 
            at identifying entry and exit points for intraday trading.''',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 4. Sentiment Agent
        sentiment_agent = Agent(
            role='Sentiment Analyst',
            goal='Analyze news and social sentiment to gauge market mood',
            backstory='''You are an expert in gauging market sentiment through news analysis, 
            social media monitoring, and understanding crowd psychology. You can identify when 
            sentiment is shifting and how it might impact prices.''',
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return {
            'fundamental': fundamental_agent,
            'economic': economic_agent,
            'technical': technical_agent,
            'sentiment': sentiment_agent
        }
    
    def _generate_ai_explanation(
        self,
        symbol: str,
        asset_class: str,
        current_price: float,
        signal: TradingSignal,
        fundamental: Dict,
        economic: Dict,
        technical: Dict,
        sentiment: Dict,
        llm=None,
    ) -> str:
        """
        Call GPT-4o to produce a single, rich plain-English paragraph that
        explains the full signal decision — what each agent found, why they
        agree or disagree, and a clear risk/reward narrative.
        """
        try:
            # Determine how many agents agree with the final signal
            analyses = [fundamental, economic, technical, sentiment]
            names = ["Fundamental", "Economic", "Technical", "Sentiment"]
            agree = [n for n, a in zip(names, analyses) if a["recommendation"] == signal.signal]
            disagree = [n for n, a in zip(names, analyses) if a["recommendation"] != signal.signal and a["recommendation"] != "NEUTRAL"]
            neutral = [n for n, a in zip(names, analyses) if a["recommendation"] == "NEUTRAL"]

            risk = abs(signal.entry_price - signal.stop_loss)
            reward = abs(signal.take_profit - signal.entry_price)
            rr = f"1:{reward / risk:.1f}" if risk > 0 else "N/A"

            prompt = f"""You are an expert trading analyst. Provide a single, confident, 3-5 sentence plain-English explanation of the following AI-generated trading signal. Write for a sophisticated trader who wants insight, not just a data dump. Be specific, use the actual numbers, and explain WHY — not just WHAT.

SIGNAL SUMMARY:
- Instrument: {symbol} ({asset_class})
- Current Price: ${current_price:.2f}
- Signal: {signal.signal}
- Entry: ${signal.entry_price:.2f} | Stop Loss: ${signal.stop_loss:.2f} | Take Profit: ${signal.take_profit:.2f}
- Risk/Reward: {rr}
- Overall Confidence: {signal.confidence:.1f}%

AGENT FINDINGS:
- Fundamental ({fundamental['recommendation']}, score {fundamental['score']:.0f}/100): {fundamental['reasoning']}
- Economic ({economic['recommendation']}, score {economic['score']:.0f}/100): {economic['reasoning']}
- Technical ({technical['recommendation']}, score {technical['score']:.0f}/100): {technical['reasoning']}
- Sentiment ({sentiment['recommendation']}, score {sentiment['score']:.0f}/100): {sentiment['reasoning']}

CONSENSUS: {', '.join(agree) if agree else 'None'} agree on {signal.signal}. {', '.join(disagree) + ' disagree.' if disagree else ''}{' ' + ', '.join(neutral) + ' are neutral.' if neutral else ''}

Write a 3-5 sentence explanation. Start directly with the insight — no preamble like "The AI system..." or "Based on the analysis...". Be direct, confident, and specific."""

            active_llm = llm if llm is not None else self.llm
            response = active_llm.invoke(prompt)
            explanation = response.content.strip()
            llm_model_name = getattr(active_llm, 'model_name', None) or getattr(active_llm, 'model', 'unknown')
            logger.info(f"AI explanation generated for {symbol} using {llm_model_name} ({len(explanation)} chars)")
            return explanation

        except Exception as e:
            used_llm = llm if llm is not None else self.llm
            llm_id = getattr(used_llm, 'model_name', None) or getattr(used_llm, 'model', 'unknown')
            logger.warning(f"AI explanation failed for {symbol} (model: {llm_id}): {e}")
            # Graceful fallback — never block signal delivery
            agents_text = ", ".join(
                f"{n}: {a['recommendation']}"
                for n, a in zip(["Fundamental", "Economic", "Technical", "Sentiment"],
                                [fundamental, economic, technical, sentiment])
            )
            return (
                f"{signal.signal} signal for {symbol} at ${signal.entry_price:.2f} "
                f"with {signal.confidence:.1f}% confidence. "
                f"Agent breakdown — {agents_text}. "
                f"Stop loss: ${signal.stop_loss:.2f} | Take profit: ${signal.take_profit:.2f}."
            )

    def generate_signal(self, instrument: str, timeframe: str = "15m", model: str = None) -> TradingSignal:
        """
        Generate trading signal for given instrument

        Args:
            instrument: Instrument name or symbol (e.g., "AAPL", "Apple")
            timeframe: Candle timeframe for technical analysis (1m, 5m, 15m, 30m, 1h, 1D)
            model: OpenAI model name to use for AI explanation (e.g. "gpt-4o", "gpt-4o-mini")

        Returns:
            TradingSignal with complete analysis
        """
        start_time = time.time()
        api_calls = 0

        # Build a per-request LLM only when the caller picks a different model.
        # The singleton self.llm is always kept as-is so FinBERT / agents are unaffected.
        if model and model != self.llm.model_name:
            if model.startswith("claude-"):
                if not settings.anthropic_api_key:
                    raise ValueError(
                        "Anthropic API key is required for Claude models. "
                        "Please set ANTHROPIC_API_KEY in your .env file."
                    )
                from langchain_anthropic import ChatAnthropic
                request_llm = ChatAnthropic(
                    model=model,
                    temperature=settings.temperature,
                    api_key=settings.anthropic_api_key,
                )
            else:
                request_llm = ChatOpenAI(
                    model=model,
                    temperature=settings.temperature,
                    api_key=settings.openai_api_key,
                )
            logger.info(f"Using per-request model: {model}")
        else:
            request_llm = None  # falls back to self.llm inside _generate_ai_explanation

        try:
            logger.info(f"Starting signal generation for: {instrument}")
            
            # Step 1: Process input
            processed_input = self.input_processor.process(instrument)
            symbol = processed_input["symbol"]
            asset_class = processed_input["asset_class"]
            current_price = processed_input["current_price"]
            
            logger.info(f"Processed input: {symbol} ({asset_class}) @ ${current_price:.2f}")
            
            # Step 2: Run all 4 analyzers in parallel using ThreadPoolExecutor
            logger.info("Running analysis agents in parallel...")

            def run_fundamental():
                return self.fundamental_analyzer.analyze(symbol, asset_class=asset_class)

            def run_economic():
                return self.economic_analyzer.analyze(symbol, asset_class=asset_class)

            def run_technical():
                return self.technical_analyzer.analyze(symbol, asset_class=asset_class, timeframe=timeframe)

            def run_sentiment():
                return self.sentiment_analyzer.analyze(symbol)

            tasks = {
                "fundamental": run_fundamental,
                "economic": run_economic,
                "technical": run_technical,
                "sentiment": run_sentiment,
            }

            results = {}
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_key = {executor.submit(fn): key for key, fn in tasks.items()}
                for future in as_completed(future_to_key):
                    key = future_to_key[future]
                    try:
                        results[key] = future.result()
                    except Exception as exc:
                        logger.error(f"{key} analyzer raised an exception: {exc}", exc_info=True)
                        # Return neutral result on failure so synthesis can continue
                        results[key] = {
                            "recommendation": "NEUTRAL",
                            "score": 50.0,
                            "reasoning": f"Analyzer error: {exc}",
                            "confidence": 0.0,
                        }

            fundamental_result = results["fundamental"]
            economic_result = results["economic"]
            technical_result = results["technical"]
            sentiment_result = results["sentiment"]
            api_calls += 7  # Approximate total across all analyzers

            logger.info("All analyzers completed (parallel)")

            # Step 3: Synthesize final signal
            logger.info("Synthesizing final signal...")
            signal = self.decision_synthesizer.synthesize(
                fundamental=fundamental_result,
                economic=economic_result,
                technical=technical_result,
                sentiment=sentiment_result,
                current_price=current_price,
                symbol=symbol,
                asset_class=asset_class
            )

            # Step 4: AI plain-English explanation (runs after synthesis so it
            # can reference the final signal direction and all 4 agent outputs)
            active_llm = request_llm if request_llm is not None else self.llm
            active_model_id = getattr(active_llm, 'model_name', None) or getattr(active_llm, 'model', 'unknown')
            logger.info(f"Generating {active_model_id} narrative explanation...")
            signal.ai_explanation = self._generate_ai_explanation(
                symbol=symbol,
                asset_class=asset_class,
                current_price=current_price,
                signal=signal,
                fundamental=fundamental_result,
                economic=economic_result,
                technical=technical_result,
                sentiment=sentiment_result,
                llm=request_llm,
            )
            api_calls += 1  # one LLM call

            # Step 5: Validate signal
            logger.info("Validating signal...")
            is_valid, error_message = self.safety_validator.validate(signal)

            if not is_valid:
                logger.warning(f"Signal validation failed: {error_message}")

            # Step 6: Add metadata
            execution_time = time.time() - start_time
            signal.execution_time = round(execution_time, 2)
            signal.api_calls_made = api_calls
            signal.asset_class = asset_class
            signal.timeframe = timeframe

            logger.info(
                f"Signal generation complete: {signal.signal} for {symbol} "
                f"(confidence: {signal.confidence}%, time: {execution_time:.2f}s)"
            )

            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}", exc_info=True)
            raise
