"""
Sentiment analysis intelligence provider.
Analyzes market sentiment for a stock using AI.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


SENTIMENT_AGENT_BACKSTORY = """You are a Market Sentiment Analyst AI specializing in gauging market sentiment from various sources.

Your responsibilities:
1. Analyze social media sentiment (Twitter, Reddit, StockTwits)
2. Evaluate analyst ratings and price targets
3. Assess institutional investor sentiment
4. Monitor retail investor activity
5. Track options flow sentiment (put/call ratios)

Provide sentiment scores and clear reasoning for your assessment."""


class SentimentProvider(IntelligenceProvider):
    """
    Provider for market sentiment analysis.
    
    Analyzes:
    - Social media sentiment
    - Analyst ratings
    - Institutional sentiment
    - Retail investor activity
    - Options flow
    """
    
    @property
    def name(self) -> str:
        return "sentiment_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.SENTIMENT
    
    @property
    def description(self) -> str:
        return "Analyzes market sentiment from social media, analysts, and trading activity"
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Analyze sentiment for a stock."""
        logger.info(f"Analyzing sentiment for {stock}")
        
        try:
            # Create sentiment agent
            agent_kwargs = {"verbose": False, "allow_delegation": False}
            if self.llm_model:
                agent_kwargs["llm"] = self.llm_model
            
            agent = Agent(
                role="Sentiment Analyst",
                goal="Analyze market sentiment and provide actionable insights",
                backstory=SENTIMENT_AGENT_BACKSTORY,
                **agent_kwargs,
            )
            
            task = Task(
                description=f"""
                Analyze the current market sentiment for {stock}.
                
                Provide:
                1. Overall sentiment score (-1 to 1, negative = bearish, positive = bullish)
                2. Social media sentiment summary
                3. Analyst consensus
                4. Key sentiment drivers
                5. Sentiment trend (improving/declining/stable)
                
                Context: {context or 'No additional context'}
                """,
                expected_output="Structured sentiment analysis with scores and reasoning",
                agent=agent,
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=False, process=Process.sequential)
            result = str(crew.kickoff())
            
            # Parse sentiment score from result
            sentiment_score = self._extract_sentiment_score(result)
            
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                data={
                    "raw_analysis": result,
                    "sentiment_score": sentiment_score,
                },
                summary=result[:500] + "..." if len(result) > 500 else result,
                confidence=0.7,
                risk_impact=sentiment_score * 0.3,  # Sentiment impacts risk moderately
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Sentiment analysis failed: {str(e)}",
                confidence=0.0,
            )
    
    def _extract_sentiment_score(self, text: str) -> float:
        """Extract sentiment score from analysis text."""
        text_lower = text.lower()
        
        # Simple heuristic - can be improved
        bullish_words = ["bullish", "positive", "optimistic", "strong", "buy"]
        bearish_words = ["bearish", "negative", "pessimistic", "weak", "sell"]
        
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        
        total = bullish_count + bearish_count
        if total == 0:
            return 0.0
        
        return (bullish_count - bearish_count) / total


