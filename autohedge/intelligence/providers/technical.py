"""
Advanced technical analysis intelligence provider.
Provides deeper technical analysis beyond basic indicators.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from loguru import logger
import yfinance as yf

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


TECHNICAL_AGENT_BACKSTORY = """You are a Technical Analysis Expert AI specializing in chart patterns and technical indicators.

Your responsibilities:
1. Identify chart patterns (head and shoulders, double tops, etc.)
2. Analyze support and resistance levels
3. Evaluate momentum indicators (RSI, MACD, Stochastic)
4. Assess volume patterns and accumulation/distribution
5. Identify trend strength and direction
6. Detect divergences between price and indicators

Provide actionable technical insights with specific price levels."""


class TechnicalProvider(IntelligenceProvider):
    """
    Provider for advanced technical analysis.
    
    Analyzes:
    - Chart patterns
    - Support/resistance levels
    - Momentum indicators
    - Volume analysis
    - Trend analysis
    - Divergences
    """
    
    @property
    def name(self) -> str:
        return "technical_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.TECHNICAL
    
    @property
    def description(self) -> str:
        return "Provides advanced technical analysis with chart patterns and indicators"
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Perform advanced technical analysis for a stock."""
        logger.info(f"Performing technical analysis for {stock}")
        
        try:
            # Get technical data
            tech_data = self._get_technical_data(stock)
            
            agent_kwargs = {"verbose": False, "allow_delegation": False}
            if self.llm_model:
                agent_kwargs["llm"] = self.llm_model
            
            agent = Agent(
                role="Technical Analyst",
                goal="Provide advanced technical analysis and trading signals",
                backstory=TECHNICAL_AGENT_BACKSTORY,
                **agent_kwargs,
            )
            
            task = Task(
                description=f"""
                Perform advanced technical analysis for {stock}.
                
                Current Technical Data:
                {tech_data}
                
                Analyze:
                1. Current trend direction and strength
                2. Key support and resistance levels
                3. Momentum indicators status
                4. Volume analysis
                5. Chart pattern identification
                6. Technical buy/sell signals
                
                Provide:
                - Technical score (-1 bearish to 1 bullish)
                - Key price levels
                - Trading signals
                - Risk/reward assessment
                
                Context: {context or 'No additional context'}
                """,
                expected_output="Structured technical analysis with specific price levels and signals",
                agent=agent,
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=False, process=Process.sequential)
            result = str(crew.kickoff())
            
            tech_score = self._assess_technical_outlook(result)
            
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                data={
                    "raw_analysis": result,
                    "technical_data": tech_data,
                    "technical_score": tech_score,
                },
                summary=result[:500] + "..." if len(result) > 500 else result,
                confidence=0.65,
                risk_impact=tech_score * 0.2,
            )
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Technical analysis failed: {str(e)}",
                confidence=0.0,
            )
    
    def _get_technical_data(self, stock: str) -> Dict[str, Any]:
        """Get technical data for analysis."""
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                return {"error": "No historical data available"}
            
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            
            # Calculate indicators
            sma_20 = close.tail(20).mean()
            sma_50 = close.tail(50).mean()
            
            # RSI calculation
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Support/Resistance
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            
            # Volume analysis
            avg_volume = volume.tail(20).mean()
            current_volume = volume.iloc[-1]
            
            return {
                "current_price": float(close.iloc[-1]),
                "sma_20": float(sma_20),
                "sma_50": float(sma_50),
                "rsi_14": float(rsi),
                "recent_high": float(recent_high),
                "recent_low": float(recent_low),
                "avg_volume": float(avg_volume),
                "volume_ratio": float(current_volume / avg_volume),
                "price_vs_sma20": float((close.iloc[-1] / sma_20 - 1) * 100),
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _assess_technical_outlook(self, text: str) -> float:
        """Assess technical outlook from analysis text."""
        text_lower = text.lower()
        
        bullish = ["bullish", "uptrend", "breakout", "support", "accumulation", "buy"]
        bearish = ["bearish", "downtrend", "breakdown", "resistance", "distribution", "sell"]
        
        bull_count = sum(1 for word in bullish if word in text_lower)
        bear_count = sum(1 for word in bearish if word in text_lower)
        
        total = bull_count + bear_count
        if total == 0:
            return 0.0
        
        return (bull_count - bear_count) / total


