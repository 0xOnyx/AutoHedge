"""
Trading cycle orchestration module.
Coordinates the complete trading cycle following the sequence diagram.

Sequence Diagram (Updated with Intelligence):
┌────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  ┌───────────┐  ┌──────────────┐
│ Client │  │ Director │  │ Quant │  │ Risk │  │ Execution │  │ Intelligence │
└───┬────┘  └────┬─────┘  └───┬───┘  └──┬───┘  └─────┬─────┘  └──────┬───────┘
    │            │            │         │            │               │
    │ Initialize │            │         │            │               │
    │───────────>│            │         │            │               │
    │            │            │         │            │               │
    │            │ Get Intel  │         │            │               │
    │            │────────────────────────────────────────────────>│
    │            │            │         │            │               │
    │            │ Intel Data │         │            │               │
    │            │<────────────────────────────────────────────────│
    │            │            │         │            │               │
    │            │ Thesis     │         │            │               │
    │            │───────┐    │         │            │               │
    │            │       │    │         │            │               │
    │            │<──────┘    │         │            │               │
    │            │            │         │            │               │
    │            │ Analysis   │         │            │               │
    │            │───────────>│         │            │               │
    │            │<───────────│         │            │               │
    │            │            │         │            │               │
    │            │ Risk + Intel Context  │            │               │
    │            │──────────────────────>│            │               │
    │            │<──────────────────────│            │               │
    │            │            │         │            │               │
    │            │ Order      │         │            │               │
    │            │───────────────────────────────>│               │
    │            │<───────────────────────────────│               │
    │            │            │         │            │               │
    │ Results    │            │         │            │               │
    │<───────────│            │         │            │               │
"""
from typing import Optional, List, Dict, Any
from crewai import Crew, Process
from loguru import logger

from autohedge.core.enums import TradingState, RiskDecision
from autohedge.core.models import StockAnalysis
from autohedge.agents.factory import AgentFactory
from autohedge.data.market import MarketDataProvider
from autohedge.trading.state_machine import TradingStateMachine
from autohedge.trading.tasks import TaskFactory


class TradingCycle:
    """
    Orchestrates a complete trading cycle for a single stock.
    
    Follows the sequence diagram and state machine patterns.
    Now supports scalable intelligence providers for enriched risk assessment.
    """
    
    def __init__(
        self,
        agent_factory: AgentFactory,
        market_data_provider: MarketDataProvider,
        intelligence_registry: Optional[Any] = None,
        max_retries: int = 3,
    ):
        """
        Initialize the trading cycle.
        
        Args:
            agent_factory: Factory for creating agents
            market_data_provider: Provider for market data
            intelligence_registry: Optional registry of intelligence providers
            max_retries: Maximum retries on risk rejection
        """
        self.agent_factory = agent_factory
        self.market_data_provider = market_data_provider
        self.intelligence_registry = intelligence_registry
        self.max_retries = max_retries
        self.state_machine = TradingStateMachine()
    
    def _create_crew(self, task) -> Crew:
        """Create a crew for executing a single task."""
        return Crew(
            agents=[task.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential,
        )
    
    def _parse_risk_decision(self, risk_assessment: str) -> RiskDecision:
        """Parse risk assessment text for approval/rejection."""
        risk_lower = risk_assessment.lower()
        if 'reject' in risk_lower or 'rejected' in risk_lower:
            return RiskDecision.REJECTED
        return RiskDecision.APPROVED
    
    def _gather_intelligence(self, stock: str, context: Dict[str, Any]) -> str:
        """
        Gather intelligence from all registered providers.
        
        Args:
            stock: Stock ticker symbol
            context: Context to pass to providers
            
        Returns:
            Aggregated intelligence context string
        """
        if self.intelligence_registry is None:
            return ""
        
        logger.info(f"Gathering intelligence for {stock}")
        return self.intelligence_registry.get_aggregated_context(stock, context)
    
    def run(self, stock: str, task: str) -> Optional[StockAnalysis]:
        """
        Execute a complete trading cycle for a stock.
        
        Args:
            stock: Stock ticker symbol
            task: Trading task description
            
        Returns:
            StockAnalysis object with results, or None if failed
        """
        logger.info(f"Starting trading cycle for {stock}")
        self.state_machine.reset()
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Step 1: Initialize (Client -> Director)
                self.state_machine.transition_to(TradingState.THESIS_GENERATION)
                market_data = self.market_data_provider.get_data(stock)
                
                # Step 1.5: Gather Intelligence (if registry available)
                intel_context = self._gather_intelligence(
                    stock,
                    {"market_data": market_data.raw, "task": task}
                )
                
                # Step 2: Generate Thesis (Director internal)
                thesis_task = TaskFactory.create_thesis_task(
                    agent=self.agent_factory.director,
                    stock=stock,
                    task_description=task,
                    market_data=market_data.formatted,
                    intelligence_context=intel_context,
                )
                thesis = str(self._create_crew(thesis_task).kickoff())
                logger.info(f"Thesis generated for {stock}")
                
                # Step 3: Request Quant Analysis (Director -> Quant)
                self.state_machine.transition_to(TradingState.QUANT_ANALYSIS)
                quant_task = TaskFactory.create_quant_task(
                    agent=self.agent_factory.quant,
                    stock=stock,
                    thesis=thesis,
                    market_data=market_data.formatted,
                    technical_indicators=market_data.raw.get('technical_indicators', {}),
                )
                quant_analysis = str(self._create_crew(quant_task).kickoff())
                logger.info(f"Quant analysis completed for {stock}")
                
                # Step 4: Request Risk Assessment (Director -> Risk)
                # Now includes intelligence context for enriched assessment
                self.state_machine.transition_to(TradingState.RISK_ASSESSMENT)
                risk_task = TaskFactory.create_risk_task(
                    agent=self.agent_factory.risk,
                    stock=stock,
                    thesis=thesis,
                    quant_analysis=quant_analysis,
                    intelligence_context=intel_context,
                )
                risk_assessment = str(self._create_crew(risk_task).kickoff())
                risk_decision = self._parse_risk_decision(risk_assessment)
                logger.info(f"Risk assessment for {stock}: {risk_decision.value}")
                
                # Check risk decision
                if risk_decision == RiskDecision.REJECTED:
                    retry_count += 1
                    logger.warning(
                        f"Risk rejected for {stock}. Retry {retry_count}/{self.max_retries}"
                    )
                    self.state_machine.handle_risk_decision(risk_decision)
                    continue
                
                # Step 5: Generate Order (Director -> Execution)
                self.state_machine.transition_to(TradingState.ORDER_GENERATION)
                execution_task = TaskFactory.create_execution_task(
                    agent=self.agent_factory.execution,
                    stock=stock,
                    thesis=thesis,
                    risk_assessment=risk_assessment,
                )
                order = str(self._create_crew(execution_task).kickoff())
                logger.info(f"Order generated for {stock}")
                
                # Step 6 & 7: Execute and Monitor (simulated)
                self.state_machine.transition_to(TradingState.ORDER_EXECUTION)
                self.state_machine.transition_to(TradingState.MONITORING)
                self.state_machine.transition_to(TradingState.COMPLETE)
                
                # Return analysis
                return StockAnalysis(
                    stock=stock,
                    thesis=thesis,
                    quant_analysis=quant_analysis,
                    risk_assessment=risk_assessment,
                    risk_decision=risk_decision.value,
                    order=order,
                    decision=f"APPROVED - Order execution simulated for {stock}",
                    state=self.state_machine.state.value,
                )
                
            except Exception as e:
                logger.error(f"Error in trading cycle for {stock}: {str(e)}")
                retry_count += 1
                if retry_count >= self.max_retries:
                    break
        
        logger.error(f"Trading cycle failed for {stock} after {self.max_retries} retries")
        return None
