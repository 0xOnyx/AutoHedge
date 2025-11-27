"""
Sector analysis intelligence provider.
Analyzes sector dynamics and competitive positioning.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


SECTOR_AGENT_BACKSTORY = """You are a Sector Analyst AI specializing in industry dynamics and competitive analysis.

Your responsibilities:
1. Analyze sector trends and growth prospects
2. Evaluate competitive positioning within the sector
3. Assess market share dynamics
4. Monitor regulatory environment
5. Track industry-specific metrics and KPIs
6. Identify sector rotation patterns

Provide insights on how sector dynamics affect the stock's investment potential."""


class SectorProvider(IntelligenceProvider):
    """
    Provider for sector and competitive analysis.
    
    Analyzes:
    - Sector trends
    - Competitive positioning
    - Market share
    - Regulatory environment
    - Industry metrics
    - Sector rotation
    """
    
    @property
    def name(self) -> str:
        return "sector_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.SECTOR
    
    @property
    def description(self) -> str:
        return "Analyzes sector dynamics and competitive positioning"
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Analyze sector dynamics for a stock."""
        logger.info(f"Analyzing sector for {stock}")
        
        try:
            agent_kwargs = {"verbose": False, "allow_delegation": False}
            if self.llm_model:
                agent_kwargs["llm"] = self.llm_model
            
            agent = Agent(
                role="Sector Analyst",
                goal="Analyze sector dynamics and competitive positioning",
                backstory=SECTOR_AGENT_BACKSTORY,
                **agent_kwargs,
            )
            
            task = Task(
                description=f"""
                Analyze sector dynamics for {stock}.
                
                Evaluate:
                1. Sector growth trajectory
                2. Company's competitive position
                3. Market share trends
                4. Barriers to entry
                5. Regulatory environment
                6. Key sector catalysts/risks
                
                Provide:
                - Sector attractiveness score (0-1)
                - Competitive strength rating
                - Key opportunities and threats
                - Sector outlook
                
                Context: {context or 'No additional context'}
                """,
                expected_output="Structured sector analysis with competitive assessment",
                agent=agent,
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=False, process=Process.sequential)
            result = str(crew.kickoff())
            
            sector_score = self._assess_sector_strength(result)
            
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                data={
                    "raw_analysis": result,
                    "sector_score": sector_score,
                },
                summary=result[:500] + "..." if len(result) > 500 else result,
                confidence=0.7,
                risk_impact=sector_score * 0.25,
            )
            
        except Exception as e:
            logger.error(f"Sector analysis failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Sector analysis failed: {str(e)}",
                confidence=0.0,
            )
    
    def _assess_sector_strength(self, text: str) -> float:
        """Assess sector strength from analysis text."""
        text_lower = text.lower()
        
        positive = ["leader", "dominant", "growing", "strong", "opportunity", "favorable"]
        negative = ["declining", "competition", "threat", "challenging", "weak", "saturated"]
        
        pos_count = sum(1 for word in positive if word in text_lower)
        neg_count = sum(1 for word in negative if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total

