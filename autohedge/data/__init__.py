"""
Data module - Handles market data retrieval and processing.
Implements the Input layer of the Data Flow diagram.

Data Flow:
Market Data -> Technical Indicators -> Fundamental Data -> Processing
"""
from autohedge.data.market import MarketDataProvider

__all__ = ["MarketDataProvider"]

