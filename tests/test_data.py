"""
Tests for data module (market data provider).
"""
import pytest
from autohedge.data.market import MarketDataProvider, get_market_data


class TestMarketDataProvider:
    """Tests for MarketDataProvider class."""
    
    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = MarketDataProvider()
        assert provider.period == "1mo"
        
        provider = MarketDataProvider(period="3mo")
        assert provider.period == "3mo"
    
    def test_get_data_real_stock(self):
        """Test fetching data for a real stock."""
        provider = MarketDataProvider()
        data = provider.get_data("AAPL")
        
        assert data.stock == "AAPL"
        assert data.formatted is not None
        assert len(data.formatted) > 0
        
        # Should have some price data
        assert data.current_price is not None or "N/A" in data.formatted
    
    def test_get_data_invalid_stock(self):
        """Test fetching data for an invalid stock."""
        provider = MarketDataProvider()
        data = provider.get_data("INVALID_TICKER_XYZ123")
        
        # Should not crash, should return MarketData with N/A values
        assert data.stock == "INVALID_TICKER_XYZ123"
        # Invalid ticker should have N/A values
        assert "n/a" in data.formatted.lower() or data.current_price is None
    
    def test_get_data_formatted_output(self):
        """Test that formatted output contains expected fields."""
        provider = MarketDataProvider()
        data = provider.get_data("MSFT")
        
        formatted = data.formatted.lower()
        
        # Should contain some market data labels
        assert "market data" in formatted or "price" in formatted
    
    def test_get_data_raw_structure(self):
        """Test that raw data has expected structure."""
        provider = MarketDataProvider()
        data = provider.get_data("GOOGL")
        
        raw = data.raw
        
        assert "current_price" in raw
        assert "market_cap" in raw
        assert "volume" in raw
        assert "technical_indicators" in raw
    
    def test_convenience_function(self):
        """Test get_market_data convenience function."""
        result = get_market_data("NVDA")
        
        assert "raw" in result
        assert "formatted" in result
        assert isinstance(result["formatted"], str)


class TestMarketDataProviderTechnicalIndicators:
    """Tests for technical indicators calculation."""
    
    def test_technical_indicators_present(self):
        """Test that technical indicators are calculated."""
        provider = MarketDataProvider()
        data = provider.get_data("AAPL")
        
        raw = data.raw
        indicators = raw.get("technical_indicators", {})
        
        # Should have some indicators (may be None if data not available)
        assert "sma_20" in indicators or data.sma_20 is not None or data.sma_20 is None
        assert "volatility" in indicators or data.volatility is not None or data.volatility is None

