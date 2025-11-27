"""
Market data provider module.
Retrieves and processes market data from external sources.

Data Flow Diagram - Input Layer:
┌─────────────────┐
│   Market Data   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│ Tech  │ │Fundamental│
│ Ind.  │ │   Data    │
└───────┘ └───────────┘
"""
from typing import Dict, Any, Optional
import yfinance as yf
from loguru import logger

from autohedge.core.models import MarketData


class MarketDataProvider:
    """
    Provider for market data using yfinance.
    Implements the Input layer of the Data Flow diagram.
    """
    
    def __init__(self, period: str = "1mo"):
        """
        Initialize the market data provider.
        
        Args:
            period: Historical data period (default: 1 month)
        """
        self.period = period
        logger.info(f"MarketDataProvider initialized with period: {period}")
    
    def get_data(self, stock: str) -> MarketData:
        """
        Retrieve market data for a given stock symbol.
        
        Args:
            stock: Stock ticker symbol
            
        Returns:
            MarketData object containing raw and formatted data
        """
        try:
            ticker = yf.Ticker(stock)
            info = ticker.info
            hist = ticker.history(period=self.period)
            
            # Extract fundamental data
            current_price = self._get_current_price(info, hist)
            market_cap = info.get('marketCap')
            volume = self._get_volume(info, hist)
            pe_ratio = info.get('trailingPE')
            
            # Calculate technical indicators
            sma_20, sma_50, volatility, variation_1m = self._calculate_indicators(hist)
            
            # Create formatted string
            formatted = self._format_data(
                stock, current_price, market_cap, volume, pe_ratio,
                sma_20, sma_50, volatility, variation_1m
            )
            
            market_data = MarketData(
                stock=stock,
                current_price=current_price,
                market_cap=market_cap,
                volume=volume,
                pe_ratio=pe_ratio,
                sma_20=sma_20,
                sma_50=sma_50,
                volatility=volatility,
                variation_1m=variation_1m,
                formatted=formatted,
            )
            
            logger.info(f"Market data retrieved for {stock}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error retrieving market data for {stock}: {str(e)}")
            return MarketData(
                stock=stock,
                formatted=f"Limited market data for {stock}. Error: {str(e)}"
            )
    
    def _get_current_price(self, info: Dict, hist) -> Optional[float]:
        """Get current price from info or historical data."""
        price = info.get('currentPrice')
        if price is None and not hist.empty:
            price = float(hist['Close'].iloc[-1])
        return price
    
    def _get_volume(self, info: Dict, hist) -> Optional[float]:
        """Get volume from info or historical data."""
        volume = info.get('volume')
        if volume is None and not hist.empty:
            volume = float(hist['Volume'].iloc[-1])
        return volume
    
    def _calculate_indicators(self, hist) -> tuple:
        """
        Calculate technical indicators from historical data.
        
        Returns:
            Tuple of (sma_20, sma_50, volatility, variation_1m)
        """
        if hist.empty:
            return None, None, None, None
        
        sma_20 = float(hist['Close'].tail(20).mean())
        sma_50 = float(hist['Close'].tail(50).mean()) if len(hist) >= 50 else None
        volatility = float(hist['Close'].pct_change().std() * (252 ** 0.5) * 100)
        
        if len(hist) > 0:
            variation_1m = float((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100)
        else:
            variation_1m = None
        
        return sma_20, sma_50, volatility, variation_1m
    
    def _format_data(
        self,
        stock: str,
        current_price: Optional[float],
        market_cap: Optional[float],
        volume: Optional[float],
        pe_ratio: Optional[float],
        sma_20: Optional[float],
        sma_50: Optional[float],
        volatility: Optional[float],
        variation_1m: Optional[float],
    ) -> str:
        """Format market data as a readable string."""
        def fmt(value, prefix="", suffix="", decimals=2):
            if value is None:
                return "N/A"
            if isinstance(value, float):
                return f"{prefix}{value:,.{decimals}f}{suffix}"
            return f"{prefix}{value}{suffix}"
        
        return f"""
Market Data for {stock}:
- Current Price: {fmt(current_price, prefix="$")}
- Market Cap: {fmt(market_cap, prefix="$", decimals=0)}
- Volume: {fmt(volume, decimals=0)}
- P/E Ratio: {fmt(pe_ratio)}
- SMA 20 days: {fmt(sma_20, prefix="$")}
- SMA 50 days: {fmt(sma_50, prefix="$")}
- Annualized Volatility: {fmt(volatility, suffix="%")}
- 1 Month Change: {fmt(variation_1m, suffix="%")}
"""


# Convenience function for backward compatibility
def get_market_data(stock: str) -> Dict[str, Any]:
    """
    Retrieve market data for a given stock symbol.
    
    Args:
        stock: Stock ticker symbol
        
    Returns:
        Dictionary with 'raw' and 'formatted' keys
    """
    provider = MarketDataProvider()
    data = provider.get_data(stock)
    return {
        'raw': data.raw,
        'formatted': data.formatted,
    }


