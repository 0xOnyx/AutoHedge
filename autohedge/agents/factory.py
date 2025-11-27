"""
Agent factory module.
Creates and configures Crew AI agents for the trading system.
"""
from typing import Optional, Dict, Any
from crewai import Agent
from loguru import logger

from autohedge.agents.prompts import (
    DIRECTOR_PROMPT,
    QUANT_PROMPT,
    RISK_PROMPT,
    EXECUTION_PROMPT,
    AgentPrompt,
)


class AgentFactory:
    """
    Factory class for creating trading system agents.
    
    Agents in the sequence diagram:
    - Director: Orchestrates the trading process
    - Quant: Provides quantitative analysis
    - Risk: Assesses and manages risks
    - Execution: Generates trade orders
    """
    
    def __init__(self, llm_model: Optional[str] = None, verbose: bool = True):
        """
        Initialize the agent factory.
        
        Args:
            llm_model: LLM model to use for agents
            verbose: Enable verbose output
        """
        self.llm_model = llm_model
        self.verbose = verbose
        self._agents: Dict[str, Agent] = {}
        
        logger.info(f"AgentFactory initialized with LLM: {llm_model or 'default'}")
    
    def _get_agent_kwargs(self) -> Dict[str, Any]:
        """Get common agent keyword arguments."""
        kwargs = {
            "verbose": self.verbose,
            "allow_delegation": False,
        }
        if self.llm_model:
            kwargs["llm"] = self.llm_model
        return kwargs
    
    def _create_agent(self, prompt: AgentPrompt) -> Agent:
        """
        Create an agent from a prompt configuration.
        
        Args:
            prompt: Agent prompt configuration
            
        Returns:
            Configured Crew AI Agent
        """
        return Agent(
            role=prompt.role,
            goal=prompt.goal,
            backstory=prompt.backstory,
            **self._get_agent_kwargs(),
        )
    
    @property
    def director(self) -> Agent:
        """
        Get or create the Director agent.
        
        Role: Orchestrate trading process, generate theses, make final decisions.
        """
        if "director" not in self._agents:
            self._agents["director"] = self._create_agent(DIRECTOR_PROMPT)
            logger.info("Director agent created")
        return self._agents["director"]
    
    @property
    def quant(self) -> Agent:
        """
        Get or create the Quant agent.
        
        Role: Provide quantitative and technical analysis.
        """
        if "quant" not in self._agents:
            self._agents["quant"] = self._create_agent(QUANT_PROMPT)
            logger.info("Quant agent created")
        return self._agents["quant"]
    
    @property
    def risk(self) -> Agent:
        """
        Get or create the Risk agent.
        
        Role: Assess risks and approve/reject trades.
        """
        if "risk" not in self._agents:
            self._agents["risk"] = self._create_agent(RISK_PROMPT)
            logger.info("Risk agent created")
        return self._agents["risk"]
    
    @property
    def execution(self) -> Agent:
        """
        Get or create the Execution agent.
        
        Role: Generate trade orders with precise parameters.
        """
        if "execution" not in self._agents:
            self._agents["execution"] = self._create_agent(EXECUTION_PROMPT)
            logger.info("Execution agent created")
        return self._agents["execution"]
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """
        Get all agents (creates them if not already created).
        
        Returns:
            Dictionary of all agents
        """
        # Access all properties to ensure agents are created
        _ = self.director
        _ = self.quant
        _ = self.risk
        _ = self.execution
        return self._agents.copy()

