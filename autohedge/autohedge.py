"""
AutoHedge - Main entry point class.
Coordinates all modules to run the trading system.

Architecture Overview:
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AutoHedge                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Config    │  │   Agents    │  │   Trading    │  │   Intelligence   │  │
│  │  (core/)    │  │ (agents/)   │  │  (trading/)  │  │ (intelligence/)  │  │
│  │             │  │             │  │              │  │                  │  │
│  │ - config    │  │ - factory   │  │ - cycle      │  │ - registry       │  │
│  │ - models    │  │ - prompts   │  │ - state      │  │ - providers:     │  │
│  │ - enums     │  │             │  │ - tasks      │  │   - sentiment    │  │
│  └─────────────┘  └─────────────┘  └──────────────┘  │   - macro        │  │
│                                                      │   - sector       │  │
│                    ┌─────────────┐                   │   - technical    │  │
│                    │    Data     │                   │   - news         │  │
│                    │   (data/)   │                   │   - custom...    │  │
│                    │ - market    │                   └──────────────────┘  │
│                    └─────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────┘

Scalable Intelligence System:
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligence Registry                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Sentiment  │  │    Macro    │  │   Sector    │  + custom   │
│  │  Provider   │  │  Provider   │  │  Provider   │  providers  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │  Aggregated Insights  │                          │
│              └───────────────────────┘                          │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │    Risk Assessment    │ <- Enhanced with intel   │
│              └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
"""
from typing import List, Optional, Union
from pathlib import Path
from loguru import logger

from autohedge.core.config import Config
from autohedge.core.models import TradingCycleResult, StockAnalysis
from autohedge.agents.factory import AgentFactory
from autohedge.data.market import MarketDataProvider
from autohedge.trading.cycle import TradingCycle
from autohedge.intelligence.registry import IntelligenceRegistry
from autohedge.intelligence.providers import (
    # Data providers (real data from internet)
    EarningsProvider,
    NewsScraperProvider,
    # AI analysis providers
    SentimentProvider,
    MacroProvider,
    SectorProvider,
    TechnicalProvider,
    NewsProvider,
)


class AutoHedge:
    """
    Main trading system that coordinates all modules.
    
    This is the primary entry point for the AutoHedge trading system.
    It orchestrates the complete trading cycle with scalable intelligence.
    
    Features:
    - Multi-agent trading analysis (Director, Quant, Risk, Execution)
    - Scalable intelligence system for enriched risk assessment
    - Pluggable providers (sentiment, macro, sector, technical, news)
    - State machine for tracking trading cycle progress
    
    Example:
        ```python
        from autohedge import AutoHedge
        
        # Basic usage
        hedge = AutoHedge(stocks=["NVDA", "TSLA"])
        results = hedge.run(task="Analyze tech stocks")
        
        # With intelligence providers
        hedge = AutoHedge(
            stocks=["NVDA"],
            enable_intelligence=True,
            intelligence_providers=["sentiment", "macro", "sector"]
        )
        results = hedge.run(task="Full analysis with market intelligence")
        ```
    """
    
    # Available intelligence providers
    AVAILABLE_PROVIDERS = {
        # Data providers (real data from internet)
        "earnings": EarningsProvider,
        "news_scraper": NewsScraperProvider,
        # AI analysis providers
        "sentiment": SentimentProvider,
        "macro": MacroProvider,
        "sector": SectorProvider,
        "technical": TechnicalProvider,
        "news": NewsProvider,
    }
    
    def __init__(
        self,
        stocks: List[str],
        name: str = "autohedge",
        description: str = "fully autonomous hedge fund",
        output_dir: str = "outputs",
        output_type: str = "str",
        max_retries: int = 3,
        llm_model: Optional[str] = None,
        enable_intelligence: bool = False,
        intelligence_providers: Optional[List[str]] = None,
    ):
        """
        Initialize the AutoHedge system.
        
        Args:
            stocks: List of stock ticker symbols to analyze
            name: Name of the trading system
            description: Description of the trading system
            output_dir: Directory for storing outputs
            output_type: Type of output ("str", "list", "dict")
            max_retries: Maximum retries if risk is rejected
            llm_model: LLM model to use (e.g., "gpt-4", "gpt-4o-mini")
            enable_intelligence: Enable intelligence providers for risk assessment
            intelligence_providers: List of providers to enable. Options:
                DATA PROVIDERS (real data from internet):
                - "earnings": Quarterly earnings and financial results
                - "news_scraper": Real financial news from Yahoo Finance
                AI PROVIDERS (LLM-powered analysis):
                - "sentiment": Market sentiment analysis
                - "macro": Macroeconomic factors
                - "sector": Sector dynamics
                - "technical": Advanced technical analysis
                - "news": AI news and events analysis
                - None (default): All providers enabled
        """
        # Store configuration
        self.config = Config(
            name=name,
            description=description,
            stocks=stocks,
            output_dir=output_dir,
            output_type=output_type,
            max_retries=max_retries,
            llm_model=llm_model,
        )
        
        # Initialize components
        self.agent_factory = AgentFactory(
            llm_model=self.config.llm_model,
            verbose=self.config.verbose,
        )
        
        self.market_data_provider = MarketDataProvider()
        
        # Initialize intelligence registry
        self.intelligence_registry: Optional[IntelligenceRegistry] = None
        if enable_intelligence:
            self._setup_intelligence(intelligence_providers)
        
        # Results storage
        self.results = TradingCycleResult(
            name=self.config.name,
            description=self.config.description,
            stocks=self.config.stocks,
        )
        
        logger.info(
            f"AutoHedge initialized: {name} | "
            f"Stocks: {stocks} | "
            f"LLM: {self.config.llm_model} | "
            f"Intelligence: {'enabled' if enable_intelligence else 'disabled'}"
        )
    
    def _setup_intelligence(self, providers: Optional[List[str]] = None) -> None:
        """
        Setup intelligence registry with specified providers.
        
        Args:
            providers: List of provider names to enable, or None for all
        """
        self.intelligence_registry = IntelligenceRegistry()
        
        # Determine which providers to enable
        if providers is None:
            providers = list(self.AVAILABLE_PROVIDERS.keys())
        
        # Register each provider
        for provider_name in providers:
            if provider_name in self.AVAILABLE_PROVIDERS:
                provider_class = self.AVAILABLE_PROVIDERS[provider_name]
                provider = provider_class(llm_model=self.config.llm_model)
                self.intelligence_registry.register(provider)
            else:
                logger.warning(f"Unknown provider: {provider_name}")
        
        logger.info(f"Intelligence providers enabled: {providers}")
    
    def add_intelligence_provider(self, provider) -> "AutoHedge":
        """
        Add a custom intelligence provider.
        
        Args:
            provider: Provider instance (must inherit from IntelligenceProvider)
            
        Returns:
            Self for chaining
        """
        if self.intelligence_registry is None:
            self.intelligence_registry = IntelligenceRegistry()
        
        self.intelligence_registry.register(provider)
        logger.info(f"Added custom provider: {provider.name}")
        return self
    
    def remove_intelligence_provider(self, name: str) -> bool:
        """
        Remove an intelligence provider by name.
        
        Args:
            name: Name of provider to remove
            
        Returns:
            True if provider was removed
        """
        if self.intelligence_registry is None:
            return False
        return self.intelligence_registry.unregister(name)
    
    def list_intelligence_providers(self) -> List[str]:
        """List all registered intelligence provider names."""
        if self.intelligence_registry is None:
            return []
        return self.intelligence_registry.list_providers()
    
    def run(self, task: str) -> Union[str, List[dict], dict]:
        """
        Execute the trading cycle for all configured stocks.
        
        This method follows the sequence diagram with intelligence:
        1. Client initializes trading cycle
        2. Gather intelligence from providers (if enabled)
        3. Director generates thesis with intel context
        4. Director requests analysis from Quant
        5. Director requests risk assessment from Risk (with intel)
        6. Director requests order generation from Execution
        7. Order execution (simulated)
        8. Return complete analysis to Client
        
        Args:
            task: Trading task description
            
        Returns:
            Results in the format specified by output_type
        """
        logger.info(f"Starting trading cycle | Task: {task}")
        
        self.results.task = task
        self.results.analyses = []
        
        for stock in self.config.stocks:
            logger.info(f"Processing: {stock}")
            
            # Create and run trading cycle
            cycle = TradingCycle(
                agent_factory=self.agent_factory,
                market_data_provider=self.market_data_provider,
                intelligence_registry=self.intelligence_registry,
                max_retries=self.config.max_retries,
            )
            
            analysis = cycle.run(stock=stock, task=task)
            
            if analysis:
                self.results.add_analysis(analysis)
                logger.info(f"Completed: {stock}")
            else:
                logger.warning(f"Failed to complete analysis for: {stock}")
        
        return self._format_output()
    
    def _format_output(self) -> Union[str, List[dict], dict]:
        """Format output based on configured output_type."""
        if self.config.output_type == "str":
            return self.results.to_string()
        elif self.config.output_type == "list":
            return [a.model_dump() for a in self.results.analyses]
        elif self.config.output_type == "dict":
            return self.results.model_dump()
        else:
            return self.results.to_string()
    
    def get_results(self) -> TradingCycleResult:
        """Get the raw results object."""
        return self.results
    
    def reset(self) -> None:
        """Reset the system for a new trading cycle."""
        self.results = TradingCycleResult(
            name=self.config.name,
            description=self.config.description,
            stocks=self.config.stocks,
        )
        logger.info("AutoHedge reset")
