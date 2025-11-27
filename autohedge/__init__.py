"""
AutoHedge - Automated Trading Insights System using Crew AI

A multi-agent trading system that provides comprehensive market analysis,
quantitative insights, risk assessment, and trade recommendations.

Architecture:
- core/: Configuration, data models, enumerations
- agents/: AI agent definitions and factory
- data/: Market data retrieval and processing
- trading/: Trading cycle orchestration and state machine
- intelligence/: Scalable intelligence providers for enriched analysis

Usage:
    from autohedge import AutoHedge
    
    # Basic usage
    hedge = AutoHedge(
        stocks=["NVDA", "TSLA", "MSFT"],
        llm_model="gpt-4o-mini"
    )
    results = hedge.run(task="Analyze AI companies")
    
    # With intelligence providers for enriched risk assessment
    hedge = AutoHedge(
        stocks=["NVDA"],
        llm_model="gpt-4o-mini",
        enable_intelligence=True,
        intelligence_providers=["sentiment", "macro", "sector"]
    )
    results = hedge.run(task="Full analysis with market intelligence")
    
    # Add custom intelligence provider
    from autohedge.intelligence import IntelligenceProvider
    
    class MyProvider(IntelligenceProvider):
        # ... implementation
        pass
    
    hedge.add_intelligence_provider(MyProvider())

For more information, see the README.md file.
"""

from autohedge.autohedge import AutoHedge
from autohedge.core import (
    Config,
    TradingState,
    RiskDecision,
    StockAnalysis,
    TradingCycleResult,
    MarketData,
)
from autohedge.agents import AgentFactory
from autohedge.data import MarketDataProvider
from autohedge.trading import TradingCycle, TradingStateMachine, TaskFactory
from autohedge.intelligence import (
    IntelligenceRegistry,
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
    # Data providers (real data)
    EarningsProvider,
    NewsScraperProvider,
    # AI providers
    SentimentProvider,
    MacroProvider,
    SectorProvider,
    TechnicalProvider,
    NewsProvider,
)

__version__ = "0.3.0"
__author__ = "The Swarm Corporation"

__all__ = [
    # Main class
    "AutoHedge",
    
    # Core
    "Config",
    "TradingState",
    "RiskDecision",
    "StockAnalysis",
    "TradingCycleResult",
    "MarketData",
    
    # Agents
    "AgentFactory",
    
    # Data
    "MarketDataProvider",
    
    # Trading
    "TradingCycle",
    "TradingStateMachine",
    "TaskFactory",
    
    # Intelligence
    "IntelligenceRegistry",
    "IntelligenceProvider",
    "IntelligenceResult",
    "IntelligenceType",
    # Data providers
    "EarningsProvider",
    "NewsScraperProvider",
    # AI providers
    "SentimentProvider",
    "MacroProvider",
    "SectorProvider",
    "TechnicalProvider",
    "NewsProvider",
]
