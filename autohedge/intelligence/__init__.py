"""
Intelligence module - Scalable system for adding market intelligence crews.

This module provides a plugin architecture for adding new intelligence providers
that enrich the risk assessment process with additional market data.

Provider Types:
===============

DATA PROVIDERS (Real Data from Internet):
- EarningsProvider: Quarterly earnings, EPS, revenue, growth metrics
- NewsScraperProvider: Real financial news from Yahoo Finance

AI ANALYSIS PROVIDERS (LLM-powered):
- SentimentProvider: Market sentiment from social media/analysts
- MacroProvider: Macroeconomic factors analysis
- SectorProvider: Sector dynamics and competition
- TechnicalProvider: Advanced technical analysis
- NewsProvider: AI-powered news sentiment analysis

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligence Registry                        │
│                                                                 │
│  DATA PROVIDERS          AI PROVIDERS                           │
│  ┌──────────────┐       ┌─────────────┐                        │
│  │   Earnings   │       │  Sentiment  │                        │
│  │  (Yahoo Fin) │       │    (LLM)    │                        │
│  └──────┬───────┘       └──────┬──────┘                        │
│         │                      │                                │
│  ┌──────┴───────┐       ┌──────┴──────┐                        │
│  │ News Scraper │       │    Macro    │   + more providers     │
│  │  (Yahoo Fin) │       │    (LLM)    │                        │
│  └──────┬───────┘       └─────────────┘                        │
│         │                                                       │
│         └────────────────────┬──────────────────────────────────┘
│                              ▼                                  │
│              ┌───────────────────────┐                          │
│              │  Aggregated Insights  │                          │
│              └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌───────────────────────┐
              │    Risk Assessment    │
              └───────────────────────┘

Usage:
    from autohedge.intelligence import IntelligenceRegistry, EarningsProvider, NewsScraperProvider
    
    # Register data providers
    registry = IntelligenceRegistry()
    registry.register(EarningsProvider())
    registry.register(NewsScraperProvider())
    
    # Get aggregated insights
    insights = registry.gather_insights(stock="NVDA")
"""
from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)
from autohedge.intelligence.registry import IntelligenceRegistry
from autohedge.intelligence.providers import (
    # Data providers
    EarningsProvider,
    NewsScraperProvider,
    # AI providers
    SentimentProvider,
    MacroProvider,
    SectorProvider,
    TechnicalProvider,
    NewsProvider,
)

__all__ = [
    # Base classes
    "IntelligenceProvider",
    "IntelligenceResult",
    "IntelligenceType",
    
    # Registry
    "IntelligenceRegistry",
    
    # Data Providers (Real Data)
    "EarningsProvider",
    "NewsScraperProvider",
    
    # AI Providers
    "SentimentProvider",
    "MacroProvider",
    "SectorProvider",
    "TechnicalProvider",
    "NewsProvider",
]
