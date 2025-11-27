"""
Task factory module.
Creates Crew AI tasks for each step of the trading cycle.
"""
from typing import Dict, Any, Optional
from crewai import Task, Agent
from loguru import logger


class TaskFactory:
    """
    Factory for creating trading cycle tasks.
    
    Each task corresponds to a step in the sequence diagram:
    Director -> Quant -> Risk -> Execution
    
    Tasks now support intelligence context for enriched decision making.
    """
    
    @staticmethod
    def create_thesis_task(
        agent: Agent,
        stock: str,
        task_description: str,
        market_data: str,
        intelligence_context: str = "",
    ) -> Task:
        """
        Create thesis generation task for Director agent.
        
        Sequence: Director -> Director (Internal)
        
        Args:
            agent: Director agent
            stock: Stock ticker symbol
            task_description: User's trading task
            market_data: Formatted market data
            intelligence_context: Additional intelligence from providers
            
        Returns:
            Configured Task
        """
        intel_section = f"""
        
ADDITIONAL MARKET INTELLIGENCE:
{intelligence_context}
""" if intelligence_context else ""
        
        return Task(
            description=f"""
            Task: {task_description}
            
            Stock: {stock}
            Market Data: {market_data}
            {intel_section}
            
            Generate a comprehensive trading thesis for {stock} including:
            - A concise market thesis
            - Key technical and fundamental factors
            - Detailed risk assessment
            - Trading parameters (entry/exit points, position sizing)
            
            Consider all available market intelligence in your analysis.
            """,
            expected_output="A complete and structured trading thesis",
            agent=agent,
        )
    
    @staticmethod
    def create_quant_task(
        agent: Agent,
        stock: str,
        thesis: str,
        market_data: str,
        technical_indicators: Dict[str, Any],
    ) -> Task:
        """
        Create quantitative analysis task for Quant agent.
        
        Sequence: Director -> Quant (Request Analysis)
        
        Args:
            agent: Quant agent
            stock: Stock ticker symbol
            thesis: Director's thesis
            market_data: Formatted market data
            technical_indicators: Technical indicator data
            
        Returns:
            Configured Task
        """
        return Task(
            description=f"""
            Stock: {stock}
            Director's Thesis: {thesis}
            Market Data: {market_data}
            Technical Indicators: {technical_indicators}
            
            Perform quantitative analysis for {stock} including:
            - Technical score (0-1)
            - Volume score (0-1)
            - Trend strength (0-1)
            - Volatility analysis
            - Probability score (0-1)
            - Key levels (support, resistance, pivot)
            """,
            expected_output="A structured quantitative analysis with scores and metrics",
            agent=agent,
        )
    
    @staticmethod
    def create_risk_task(
        agent: Agent,
        stock: str,
        thesis: str,
        quant_analysis: str,
        intelligence_context: str = "",
    ) -> Task:
        """
        Create risk assessment task for Risk agent.
        
        Sequence: Director -> Risk (Request Risk Assessment)
        
        Now includes intelligence context for comprehensive risk evaluation.
        
        Args:
            agent: Risk agent
            stock: Stock ticker symbol
            thesis: Director's thesis
            quant_analysis: Quant agent's analysis
            intelligence_context: Additional intelligence from providers
            
        Returns:
            Configured Task
        """
        intel_section = f"""
        
ADDITIONAL MARKET INTELLIGENCE FOR RISK ASSESSMENT:
{intelligence_context}

Consider the above intelligence when evaluating risk factors.
""" if intelligence_context else ""
        
        return Task(
            description=f"""
            Stock: {stock}
            Thesis: {thesis}
            Quantitative Analysis: {quant_analysis}
            {intel_section}
            
            Provide comprehensive risk assessment including:
            1. Recommended position size
            2. Maximum drawdown risk
            3. Market risk exposure
            4. Sentiment risk (if data available)
            5. Macro risk factors (if data available)
            6. Sector-specific risks (if data available)
            7. Overall risk score
            
            IMPORTANT: At the end, clearly state APPROVED or REJECTED.
            """,
            expected_output="A structured risk assessment with recommendations and APPROVED/REJECTED decision",
            agent=agent,
        )
    
    @staticmethod
    def create_execution_task(
        agent: Agent,
        stock: str,
        thesis: str,
        risk_assessment: str,
    ) -> Task:
        """
        Create order generation task for Execution agent.
        
        Sequence: Director -> Execution (Generate Order)
        
        Args:
            agent: Execution agent
            stock: Stock ticker symbol
            thesis: Director's thesis
            risk_assessment: Risk agent's assessment
            
        Returns:
            Configured Task
        """
        return Task(
            description=f"""
            Stock: {stock}
            Thesis: {thesis}
            Risk Assessment: {risk_assessment}
            
            Generate a trade order including:
            1. Order type (market/limit)
            2. Quantity
            3. Entry price
            4. Stop loss
            5. Take profit
            6. Time in force
            """,
            expected_output="A structured trade order with all parameters",
            agent=agent,
        )
