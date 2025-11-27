"""
Tests for main AutoHedge class.
"""
import pytest
from autohedge import AutoHedge
from autohedge.intelligence import EarningsProvider, NewsScraperProvider


class TestAutoHedgeInitialization:
    """Tests for AutoHedge initialization."""
    
    def test_basic_initialization(self):
        """Test basic initialization."""
        hedge = AutoHedge(stocks=["NVDA"])
        
        assert hedge.config.stocks == ["NVDA"]
        assert hedge.config.name == "autohedge"
        assert hedge.intelligence_registry is None
    
    def test_custom_initialization(self):
        """Test custom initialization."""
        hedge = AutoHedge(
            stocks=["NVDA", "TSLA"],
            name="test-fund",
            description="Test fund",
            llm_model="gpt-4",
            max_retries=5,
        )
        
        assert hedge.config.stocks == ["NVDA", "TSLA"]
        assert hedge.config.name == "test-fund"
        assert hedge.config.llm_model == "gpt-4"
        assert hedge.config.max_retries == 5
    
    def test_with_intelligence_enabled(self):
        """Test initialization with intelligence enabled."""
        hedge = AutoHedge(
            stocks=["NVDA"],
            enable_intelligence=True,
            intelligence_providers=["earnings", "news_scraper"],
        )
        
        assert hedge.intelligence_registry is not None
        providers = hedge.list_intelligence_providers()
        assert "earnings_analyzer" in providers
        assert "news_scraper" in providers
    
    def test_with_all_providers(self):
        """Test initialization with all providers."""
        hedge = AutoHedge(
            stocks=["NVDA"],
            enable_intelligence=True,
            intelligence_providers=None,  # All providers
        )
        
        providers = hedge.list_intelligence_providers()
        
        # Should have multiple providers
        assert len(providers) >= 5


class TestAutoHedgeProviderManagement:
    """Tests for provider management methods."""
    
    def test_add_intelligence_provider(self):
        """Test adding an intelligence provider."""
        hedge = AutoHedge(stocks=["NVDA"])
        
        hedge.add_intelligence_provider(EarningsProvider())
        
        assert "earnings_analyzer" in hedge.list_intelligence_providers()
    
    def test_remove_intelligence_provider(self):
        """Test removing an intelligence provider."""
        hedge = AutoHedge(
            stocks=["NVDA"],
            enable_intelligence=True,
            intelligence_providers=["earnings", "news_scraper"],
        )
        
        result = hedge.remove_intelligence_provider("earnings_analyzer")
        
        assert result is True
        assert "earnings_analyzer" not in hedge.list_intelligence_providers()
    
    def test_list_intelligence_providers_empty(self):
        """Test listing providers when empty."""
        hedge = AutoHedge(stocks=["NVDA"], enable_intelligence=False)
        
        providers = hedge.list_intelligence_providers()
        
        assert providers == []
    
    def test_add_provider_chaining(self):
        """Test add_intelligence_provider returns self."""
        hedge = AutoHedge(stocks=["NVDA"])
        
        result = hedge.add_intelligence_provider(EarningsProvider())
        
        assert result is hedge


class TestAutoHedgeConfiguration:
    """Tests for AutoHedge configuration."""
    
    def test_available_providers(self):
        """Test available providers class variable."""
        assert "earnings" in AutoHedge.AVAILABLE_PROVIDERS
        assert "news_scraper" in AutoHedge.AVAILABLE_PROVIDERS
        assert "sentiment" in AutoHedge.AVAILABLE_PROVIDERS
        assert "macro" in AutoHedge.AVAILABLE_PROVIDERS
        assert "sector" in AutoHedge.AVAILABLE_PROVIDERS
        assert "technical" in AutoHedge.AVAILABLE_PROVIDERS
        assert "news" in AutoHedge.AVAILABLE_PROVIDERS
    
    def test_output_types(self):
        """Test different output types."""
        for output_type in ["str", "list", "dict"]:
            hedge = AutoHedge(stocks=["NVDA"], output_type=output_type)
            assert hedge.config.output_type == output_type
    
    def test_get_results(self):
        """Test get_results method."""
        hedge = AutoHedge(stocks=["NVDA"])
        
        results = hedge.get_results()
        
        assert results is not None
        assert results.stocks == ["NVDA"]
    
    def test_reset(self):
        """Test reset method."""
        hedge = AutoHedge(stocks=["NVDA"], name="test-fund")
        
        # Modify results
        hedge.results.task = "Test task"
        
        # Reset
        hedge.reset()
        
        assert hedge.results.task is None
        assert hedge.results.analyses == []


class TestAutoHedgeIntegration:
    """Integration tests for AutoHedge (requires API key, skipped by default)."""
    
    @pytest.mark.skip(reason="Requires OPENAI_API_KEY and makes real API calls")
    def test_run_basic(self):
        """Test basic run execution."""
        hedge = AutoHedge(
            stocks=["NVDA"],
            llm_model="gpt-4o-mini",
            enable_intelligence=False,
        )
        
        results = hedge.run(task="Analyze NVIDIA stock")
        
        assert results is not None
        assert len(results) > 0
    
    @pytest.mark.skip(reason="Requires OPENAI_API_KEY and makes real API calls")
    def test_run_with_intelligence(self):
        """Test run with intelligence providers."""
        hedge = AutoHedge(
            stocks=["NVDA"],
            llm_model="gpt-4o-mini",
            enable_intelligence=True,
            intelligence_providers=["earnings", "news_scraper"],
        )
        
        results = hedge.run(task="Analyze NVIDIA with earnings data")
        
        assert results is not None


