"""
News analysis intelligence provider.
Analyzes recent news and events affecting the stock.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


NEWS_AGENT_BACKSTORY = """You are a Financial News Analyst AI specializing in analyzing news impact on stock prices.

Your responsibilities:
1. Analyze recent company news and press releases
2. Evaluate earnings reports and guidance
3. Monitor executive changes and insider activity
4. Track regulatory filings and legal issues
5. Assess M&A activity and strategic partnerships
6. Identify catalyst events and their potential impact

Provide objective analysis of how news events affect the stock's risk profile."""


class NewsProvider(IntelligenceProvider):
    """
    Provider for news and event analysis.
    
    Analyzes:
    - Company news
    - Earnings reports
    - Executive changes
    - Regulatory filings
    - M&A activity
    - Catalyst events
    """
    
    @property
    def name(self) -> str:
        return "news_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.NEWS
    
    @property
    def description(self) -> str:
        return "Analyzes news events and their impact on stock performance"
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Analyze news for a stock."""
        logger.info(f"Analyzing news for {stock}")
        
        try:
            agent_kwargs = {"verbose": False, "allow_delegation": False}
            if self.llm_model:
                agent_kwargs["llm"] = self.llm_model
            
            agent = Agent(
                role="News Analyst",
                goal="Analyze news events and their market impact",
                backstory=NEWS_AGENT_BACKSTORY,
                **agent_kwargs,
            )
            
            task = Task(
                description=f"""
                Analyze recent news and events for {stock}.
                
                Evaluate:
                1. Recent significant news events
                2. Earnings reports and guidance updates
                3. Management changes or insider activity
                4. Regulatory or legal developments
                5. Strategic initiatives or partnerships
                6. Upcoming catalysts
                
                Provide:
                - News sentiment score (-1 to 1)
                - Key news highlights
                - Potential catalysts
                - Risk events to monitor
                
                Context: {context or 'No additional context'}
                """,
                expected_output="Structured news analysis with impact assessment",
                agent=agent,
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=False, process=Process.sequential)
            result = str(crew.kickoff())
            
            news_sentiment = self._assess_news_sentiment(result)
            
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                data={
                    "raw_analysis": result,
                    "news_sentiment": news_sentiment,
                },
                summary=result[:500] + "..." if len(result) > 500 else result,
                confidence=0.6,
                risk_impact=news_sentiment * 0.35,
            )
            
        except Exception as e:
            logger.error(f"News analysis failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"News analysis failed: {str(e)}",
                confidence=0.0,
            )
    
    def _assess_news_sentiment(self, text: str) -> float:
        """Assess news sentiment from analysis text."""
        text_lower = text.lower()
        
        positive = ["positive", "growth", "beat", "upgrade", "partnership", "expansion"]
        negative = ["negative", "miss", "downgrade", "lawsuit", "investigation", "decline"]
        
        pos_count = sum(1 for word in positive if word in text_lower)
        neg_count = sum(1 for word in negative if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total


