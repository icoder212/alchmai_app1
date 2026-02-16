"""CrewAI orchestrator for multi-agent trading signal generation"""
import time
import asyncio
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
    
    def generate_signal(self, instrument: str) -> TradingSignal:
        """
        Generate trading signal for given instrument
        
        Args:
            instrument: Instrument name or symbol (e.g., "AAPL", "Apple")
            
        Returns:
            TradingSignal with complete analysis
        """
        start_time = time.time()
        api_calls = 0
        
        try:
            logger.info(f"Starting signal generation for: {instrument}")
            
            # Step 1: Process input
            processed_input = self.input_processor.process(instrument)
            symbol = processed_input["symbol"]
            asset_class = processed_input["asset_class"]
            current_price = processed_input["current_price"]
            
            logger.info(f"Processed input: {symbol} ({asset_class}) @ ${current_price:.2f}")
            
            # Step 2: Run analyzers in parallel (simulated with sequential for now)
            logger.info("Running analysis agents...")
            
            # Run all analyzers
            fundamental_result = self.fundamental_analyzer.analyze(
                symbol, asset_class=asset_class
            )
            api_calls += 2  # Approximate
            
            economic_result = self.economic_analyzer.analyze(
                symbol, asset_class=asset_class
            )
            api_calls += 1  # FRED calls
            
            technical_result = self.technical_analyzer.analyze(symbol, asset_class=asset_class)
            api_calls += 2  # Price data calls
            
            sentiment_result = self.sentiment_analyzer.analyze(symbol)
            api_calls += 2  # News calls
            
            logger.info("All analyzers completed")
            
            # Step 3: Enhance with CrewAI agents (optional, for LLM reasoning)
            # For now, we'll use the analyzer results directly
            # In future, can add CrewAI tasks to enhance reasoning
            
            # Step 4: Synthesize final signal
            logger.info("Synthesizing final signal...")
            signal = self.decision_synthesizer.synthesize(
                fundamental=fundamental_result,
                economic=economic_result,
                technical=technical_result,
                sentiment=sentiment_result,
                current_price=current_price,
                symbol=symbol
            )
            
            # Step 5: Validate signal
            logger.info("Validating signal...")
            is_valid, error_message = self.safety_validator.validate(signal)
            
            if not is_valid:
                logger.warning(f"Signal validation failed: {error_message}")
                # Still return signal but log the issue
                # In production, might want to reject or flag
            
            # Step 6: Add metadata
            execution_time = time.time() - start_time
            signal.execution_time = round(execution_time, 2)
            signal.api_calls_made = api_calls
            signal.asset_class = asset_class
            
            logger.info(
                f"Signal generation complete: {signal.signal} for {symbol} "
                f"(confidence: {signal.confidence}%, time: {execution_time:.2f}s)"
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}", exc_info=True)
            raise
