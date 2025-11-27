"""
Macroeconomic intelligence provider.
Analyzes macroeconomic factors affecting the stock.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


MACRO_AGENT_BACKSTORY = """You are a Macroeconomic Analyst AI specializing in understanding how macro factors affect individual stocks.

Your responsibilities:
1. Analyze interest rate environment and Fed policy
2. Evaluate inflation trends and their impact
3. Assess GDP growth and economic cycle position
4. Monitor currency movements and their effects
5. Track commodity prices relevant to the stock
6. Analyze geopolitical risks

Provide clear insights on how macro factors impact the stock's risk profile."""


class MacroProvider(IntelligenceProvider):
    """
    Provider for macroeconomic analysis.
    
    Analyzes:
    - Interest rates and Fed policy
    - Inflation trends
    - Economic cycle
    - Currency movements
    - Commodity prices
    - Geopolitical risks
    """
    
    @property
    def name(self) -> str:
        return "macro_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.MACRO
    
    @property
    def description(self) -> str:
        return "Analyzes macroeconomic factors and their impact on stock performance"
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Analyze macroeconomic factors for a stock."""
        logger.info(f"Analyzing macro factors for {stock}")
        
        try:
            agent_kwargs = {"verbose": False, "allow_delegation": False}
            if self.llm_model:
                agent_kwargs["llm"] = self.llm_model
            
            agent = Agent(
                role="Macroeconomic Analyst",
                goal="Analyze macroeconomic factors affecting stock performance",
                backstory=MACRO_AGENT_BACKSTORY,
                **agent_kwargs,
            )
            
            task = Task(
                description=f"""
                Analyze macroeconomic factors affecting {stock}.
                
                Evaluate:
                1. Interest rate environment impact
                2. Inflation impact on the company
                3. Economic cycle sensitivity
                4. Currency exposure
                5. Commodity price sensitivity (if applicable)
                6. Geopolitical risk exposure
                
                Provide:
                - Overall macro risk score (-1 to 1)
                - Key macro risks
                - Macro tailwinds
                - Economic cycle positioning
                
                Context: {context or 'No additional context'}
                """,
                expected_output="Structured macro analysis with risk assessment",
                agent=agent,
            )
            
            crew = Crew(agents=[agent], tasks=[task], verbose=False, process=Process.sequential)
            result = str(crew.kickoff())
            
            macro_risk = self._assess_macro_risk(result)
            
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                data={
                    "raw_analysis": result,
                    "macro_risk_score": macro_risk,
                },
                summary=result[:500] + "..." if len(result) > 500 else result,
                confidence=0.75,
                risk_impact=macro_risk * 0.4,  # Macro has significant risk impact
            )
            
        except Exception as e:
            logger.error(f"Macro analysis failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Macro analysis failed: {str(e)}",
                confidence=0.0,
            )
    
    def _assess_macro_risk(self, text: str) -> float:
        """Assess macro risk from analysis text."""
        text_lower = text.lower()
        
        risk_words = ["risk", "threat", "headwind", "concern", "challenge", "uncertain"]
        tailwind_words = ["tailwind", "favorable", "supportive", "benefit", "opportunity"]
        
        risk_count = sum(1 for word in risk_words if word in text_lower)
        tailwind_count = sum(1 for word in tailwind_words if word in text_lower)
        
        total = risk_count + tailwind_count
        if total == 0:
            return 0.0
        
        return (tailwind_count - risk_count) / total


