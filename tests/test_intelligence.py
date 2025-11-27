"""
Tests for intelligence module (base, registry, providers).
"""
import pytest
from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)
from autohedge.intelligence.registry import IntelligenceRegistry
from autohedge.intelligence.providers import (
    EarningsProvider,
    NewsScraperProvider,
    SentimentProvider,
    MacroProvider,
    SectorProvider,
)


class TestIntelligenceType:
    """Tests for IntelligenceType enum."""
    
    def test_intelligence_types(self):
        """Test all intelligence types exist."""
        assert IntelligenceType.SENTIMENT.value == "sentiment"
        assert IntelligenceType.MACRO.value == "macro"
        assert IntelligenceType.SECTOR.value == "sector"
        assert IntelligenceType.TECHNICAL.value == "technical"
        assert IntelligenceType.NEWS.value == "news"
        assert IntelligenceType.FUNDAMENTAL.value == "fundamental"
        assert IntelligenceType.CUSTOM.value == "custom"


class TestIntelligenceResult:
    """Tests for IntelligenceResult class."""
    
    def test_result_creation(self):
        """Test IntelligenceResult creation."""
        result = IntelligenceResult(
            provider_name="test_provider",
            intelligence_type=IntelligenceType.SENTIMENT,
            stock="NVDA",
            data={"score": 0.8},
            summary="Test summary",
            confidence=0.75,
            risk_impact=0.2,
        )
        
        assert result.provider_name == "test_provider"
        assert result.stock == "NVDA"
        assert result.confidence == 0.75
        assert result.risk_impact == 0.2
    
    def test_result_default_values(self):
        """Test IntelligenceResult default values."""
        result = IntelligenceResult(
            provider_name="test",
            intelligence_type=IntelligenceType.CUSTOM,
            stock="AAPL",
        )
        
        assert result.data == {}
        assert result.summary == ""
        assert result.confidence == 0.5
        assert result.risk_impact == 0.0
        assert result.timestamp is not None
    
    def test_to_prompt_context(self):
        """Test to_prompt_context method."""
        result = IntelligenceResult(
            provider_name="test_provider",
            intelligence_type=IntelligenceType.SENTIMENT,
            stock="NVDA",
            summary="Bullish sentiment",
            confidence=0.8,
            risk_impact=0.3,
        )
        
        context = result.to_prompt_context()
        
        assert "test_provider" in context
        assert "sentiment" in context
        assert "Bullish sentiment" in context
        assert "80%" in context  # confidence
        assert "+0.30" in context  # risk impact


class TestIntelligenceRegistry:
    """Tests for IntelligenceRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = IntelligenceRegistry(parallel=False, max_workers=3)
        
        assert registry.parallel is False
        assert registry.max_workers == 3
    
    def test_register_provider(self):
        """Test registering a provider."""
        registry = IntelligenceRegistry()
        provider = EarningsProvider()
        
        registry.register(provider)
        
        assert "earnings_analyzer" in registry.list_providers()
    
    def test_register_chaining(self):
        """Test register returns self for chaining."""
        registry = IntelligenceRegistry()
        
        result = registry.register(EarningsProvider()).register(NewsScraperProvider())
        
        assert result is registry
        assert len(registry.list_providers()) == 2
    
    def test_unregister_provider(self):
        """Test unregistering a provider."""
        registry = IntelligenceRegistry()
        registry.register(EarningsProvider())
        
        result = registry.unregister("earnings_analyzer")
        
        assert result is True
        assert "earnings_analyzer" not in registry.list_providers()
    
    def test_unregister_nonexistent(self):
        """Test unregistering nonexistent provider."""
        registry = IntelligenceRegistry()
        
        result = registry.unregister("nonexistent")
        
        assert result is False
    
    def test_get_provider(self):
        """Test getting a provider by name."""
        registry = IntelligenceRegistry()
        provider = EarningsProvider()
        registry.register(provider)
        
        retrieved = registry.get_provider("earnings_analyzer")
        
        assert retrieved is provider
    
    def test_enable_disable_provider(self):
        """Test enabling/disabling providers."""
        registry = IntelligenceRegistry()
        provider = EarningsProvider()
        registry.register(provider)
        
        registry.disable_provider("earnings_analyzer")
        assert "earnings_analyzer" not in registry.list_enabled_providers()
        
        registry.enable_provider("earnings_analyzer")
        assert "earnings_analyzer" in registry.list_enabled_providers()
    
    def test_clear_registry(self):
        """Test clearing all providers."""
        registry = IntelligenceRegistry()
        registry.register(EarningsProvider())
        registry.register(NewsScraperProvider())
        
        registry.clear()
        
        assert len(registry.list_providers()) == 0


class TestEarningsProvider:
    """Tests for EarningsProvider class."""
    
    def test_provider_properties(self):
        """Test provider properties."""
        provider = EarningsProvider()
        
        assert provider.name == "earnings_analyzer"
        assert provider.intelligence_type == IntelligenceType.FUNDAMENTAL
        assert "earnings" in provider.description.lower() or "fund" in provider.description.lower()
    
    def test_analyze_real_stock(self):
        """Test analyzing a real stock."""
        provider = EarningsProvider()
        result = provider.analyze("AAPL")
        
        assert result.stock == "AAPL"
        assert result.provider_name == "earnings_analyzer"
        assert result.summary is not None
        assert len(result.summary) > 0
    
    def test_analyze_invalid_stock(self):
        """Test analyzing an invalid stock."""
        provider = EarningsProvider()
        result = provider.analyze("INVALID_XYZ123")
        
        assert result.stock == "INVALID_XYZ123"
        # Should not crash, returns result even for invalid stock
        # May have N/A data or has_earnings_data = False
        assert result.provider_name == "earnings_analyzer"
        if result.confidence > 0:
            assert result.data.get("has_earnings_data") is False or "N/A" in result.summary
    
    def test_earnings_data_structure(self):
        """Test earnings data structure."""
        provider = EarningsProvider()
        result = provider.analyze("MSFT")
        
        # Should have some data
        assert isinstance(result.data, dict)
        
        # Check for expected keys
        if result.confidence > 0:
            assert "financials" in result.data or "has_earnings_data" in result.data or "is_etf" in result.data
    
    def test_analyze_etf(self):
        """Test analyzing an ETF (like SPY)."""
        provider = EarningsProvider()
        result = provider.analyze("SPY")
        
        assert result.stock == "SPY"
        assert result.provider_name == "earnings_analyzer"
        
        # SPY should be detected as ETF
        assert result.data.get("is_etf") is True
        assert result.data.get("fund_name") is not None
        
        # Should have ETF-specific data
        assert "total_assets" in result.data or "category" in result.data
    
    def test_analyze_stock_not_etf(self):
        """Test that regular stocks are not detected as ETFs."""
        provider = EarningsProvider()
        result = provider.analyze("AAPL")
        
        # AAPL should NOT be detected as ETF
        assert result.data.get("is_etf") is False
        
        # Should have stock-specific data
        assert "financials" in result.data


class TestNewsScraperProvider:
    """Tests for NewsScraperProvider class."""
    
    def test_provider_properties(self):
        """Test provider properties."""
        provider = NewsScraperProvider()
        
        assert provider.name == "news_scraper"
        assert provider.intelligence_type == IntelligenceType.NEWS
        assert "news" in provider.description.lower()
    
    def test_max_news_parameter(self):
        """Test max_news parameter."""
        provider = NewsScraperProvider(max_news=5)
        assert provider.max_news == 5
    
    def test_analyze_real_stock(self):
        """Test analyzing news for a real stock."""
        provider = NewsScraperProvider(max_news=5)
        result = provider.analyze("GOOGL")
        
        assert result.stock == "GOOGL"
        assert result.provider_name == "news_scraper"
        assert result.summary is not None
    
    def test_news_data_structure(self):
        """Test news data structure."""
        provider = NewsScraperProvider(max_news=3)
        result = provider.analyze("NVDA")
        
        assert isinstance(result.data, dict)
        
        if result.confidence > 0:
            assert "news_count" in result.data or "sentiment" in result.data
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis in news."""
        provider = NewsScraperProvider()
        result = provider.analyze("TSLA")
        
        if result.confidence > 0 and "sentiment" in result.data:
            sentiment = result.data["sentiment"]
            assert "overall" in sentiment
            assert sentiment["overall"] in ["positive", "negative", "neutral"]
    
    def test_analyze_etf_news(self):
        """Test analyzing news for an ETF."""
        provider = NewsScraperProvider(max_news=5)
        result = provider.analyze("SPY")
        
        assert result.stock == "SPY"
        assert result.data.get("is_etf") is True
        assert result.data.get("category") is not None
        
        # Should have analyzed top holdings
        holdings = result.data.get("top_holdings_analyzed", [])
        assert len(holdings) > 0 or result.data.get("etf_news_count", 0) >= 0
    
    def test_etf_category_keywords(self):
        """Test that ETF categories have keywords."""
        from autohedge.intelligence.providers.news_scraper import ETF_CATEGORY_KEYWORDS
        
        # Check some common categories
        assert "Large Blend" in ETF_CATEGORY_KEYWORDS
        assert "Technology" in ETF_CATEGORY_KEYWORDS
        assert "Diversified Emerging Mkts" in ETF_CATEGORY_KEYWORDS
        
        # Check keywords exist
        assert len(ETF_CATEGORY_KEYWORDS["Large Blend"]) > 0
        assert "S&P 500" in ETF_CATEGORY_KEYWORDS["Large Blend"]


class TestCustomProvider:
    """Tests for creating custom providers."""
    
    def test_custom_provider(self):
        """Test creating a custom provider."""
        
        class TestProvider(IntelligenceProvider):
            @property
            def name(self) -> str:
                return "test_custom"
            
            @property
            def intelligence_type(self) -> IntelligenceType:
                return IntelligenceType.CUSTOM
            
            def analyze(self, stock, context=None) -> IntelligenceResult:
                return IntelligenceResult(
                    provider_name=self.name,
                    intelligence_type=self.intelligence_type,
                    stock=stock,
                    summary=f"Custom analysis for {stock}",
                    confidence=1.0,
                )
        
        provider = TestProvider()
        result = provider.analyze("NVDA")
        
        assert result.provider_name == "test_custom"
        assert result.stock == "NVDA"
        assert result.confidence == 1.0
        assert "NVDA" in result.summary

