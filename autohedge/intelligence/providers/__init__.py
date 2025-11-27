"""
Intelligence providers package.
Contains ready-to-use intelligence providers.

Data Providers (Real Data from Internet):
- EarningsProvider: Quarterly earnings and financial results
- NewsScraperProvider: Real financial news from Yahoo Finance

AI Analysis Providers (LLM-powered):
- SentimentProvider: Market sentiment analysis
- MacroProvider: Macroeconomic factors
- SectorProvider: Sector dynamics
- TechnicalProvider: Advanced technical analysis
- NewsProvider: AI-powered news analysis
"""
# Data providers (fetch real data)
from autohedge.intelligence.providers.earnings import EarningsProvider
from autohedge.intelligence.providers.news_scraper import NewsScraperProvider

# AI analysis providers
from autohedge.intelligence.providers.sentiment import SentimentProvider
from autohedge.intelligence.providers.macro import MacroProvider
from autohedge.intelligence.providers.sector import SectorProvider
from autohedge.intelligence.providers.technical import TechnicalProvider
from autohedge.intelligence.providers.news import NewsProvider

__all__ = [
    # Data providers
    "EarningsProvider",
    "NewsScraperProvider",
    
    # AI analysis providers
    "SentimentProvider",
    "MacroProvider",
    "SectorProvider",
    "TechnicalProvider",
    "NewsProvider",
]
