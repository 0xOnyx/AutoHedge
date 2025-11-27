"""
Tests for core module (config, enums, models).
"""
import pytest
from datetime import datetime

from autohedge.core.config import Config
from autohedge.core.enums import TradingState, RiskDecision
from autohedge.core.models import MarketData, StockAnalysis, TradingCycleResult


class TestConfig:
    """Tests for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.name == "autohedge"
        assert config.description == "fully autonomous hedge fund"
        assert config.stocks == []
        assert config.output_dir == "outputs"
        assert config.output_type == "str"
        assert config.max_retries == 3
        assert config.llm_model == "gpt-4o-mini"  # Default model
        assert config.verbose is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            name="test-fund",
            stocks=["NVDA", "TSLA"],
            llm_model="gpt-4",
            max_retries=5,
        )
        
        assert config.name == "test-fund"
        assert config.stocks == ["NVDA", "TSLA"]
        assert config.llm_model == "gpt-4"
        assert config.max_retries == 5
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "name": "dict-fund",
            "stocks": ["AAPL"],
            "llm_model": "claude-3-sonnet",
        }
        
        config = Config.from_dict(data)
        
        assert config.name == "dict-fund"
        assert config.stocks == ["AAPL"]
        assert config.llm_model == "claude-3-sonnet"
    
    def test_supported_models(self):
        """Test supported models reference."""
        assert "openai" in Config.SUPPORTED_MODELS
        assert "anthropic" in Config.SUPPORTED_MODELS
        assert "google" in Config.SUPPORTED_MODELS
        
        assert "gpt-4" in Config.SUPPORTED_MODELS["openai"]
        assert "claude-3-opus" in Config.SUPPORTED_MODELS["anthropic"]


class TestEnums:
    """Tests for enum classes."""
    
    def test_trading_state_values(self):
        """Test TradingState enum values."""
        assert TradingState.INITIALIZATION.value == "initialization"
        assert TradingState.THESIS_GENERATION.value == "thesis_generation"
        assert TradingState.QUANT_ANALYSIS.value == "quant_analysis"
        assert TradingState.RISK_ASSESSMENT.value == "risk_assessment"
        assert TradingState.ORDER_GENERATION.value == "order_generation"
        assert TradingState.ORDER_EXECUTION.value == "order_execution"
        assert TradingState.MONITORING.value == "monitoring"
        assert TradingState.COMPLETE.value == "complete"
    
    def test_risk_decision_values(self):
        """Test RiskDecision enum values."""
        assert RiskDecision.APPROVED.value == "approved"
        assert RiskDecision.REJECTED.value == "rejected"
    
    def test_enum_string_comparison(self):
        """Test enum string comparison."""
        state = TradingState.INITIALIZATION
        assert state == "initialization"
        
        decision = RiskDecision.APPROVED
        assert decision == "approved"


class TestMarketData:
    """Tests for MarketData model."""
    
    def test_market_data_creation(self):
        """Test MarketData creation."""
        data = MarketData(
            stock="NVDA",
            current_price=500.0,
            market_cap=1200000000000,
            volume=50000000,
            pe_ratio=65.5,
            sma_20=490.0,
            volatility=35.5,
            formatted="Test formatted data",
        )
        
        assert data.stock == "NVDA"
        assert data.current_price == 500.0
        assert data.market_cap == 1200000000000
        assert data.formatted == "Test formatted data"
    
    def test_market_data_raw_property(self):
        """Test MarketData raw property."""
        data = MarketData(
            stock="TSLA",
            current_price=250.0,
            sma_20=240.0,
            volatility=45.0,
        )
        
        raw = data.raw
        
        assert raw["current_price"] == 250.0
        assert raw["technical_indicators"]["sma_20"] == 240.0
        assert raw["technical_indicators"]["volatility"] == 45.0
    
    def test_market_data_timestamp(self):
        """Test MarketData auto timestamp."""
        data = MarketData(stock="AAPL")
        
        assert data.timestamp is not None
        # Should be valid ISO format
        datetime.fromisoformat(data.timestamp)


class TestStockAnalysis:
    """Tests for StockAnalysis model."""
    
    def test_stock_analysis_creation(self):
        """Test StockAnalysis creation."""
        analysis = StockAnalysis(
            stock="NVDA",
            thesis="Buy thesis",
            quant_analysis="Quant results",
            risk_assessment="Risk approved",
            risk_decision="approved",
            order="Buy 100 shares",
            decision="Execute order",
            state="complete",
        )
        
        assert analysis.stock == "NVDA"
        assert analysis.thesis == "Buy thesis"
        assert analysis.risk_decision == "approved"
        assert analysis.state == "complete"
    
    def test_stock_analysis_auto_id(self):
        """Test StockAnalysis auto-generated ID."""
        analysis1 = StockAnalysis(stock="NVDA")
        analysis2 = StockAnalysis(stock="TSLA")
        
        assert analysis1.id is not None
        assert analysis2.id is not None
        assert analysis1.id != analysis2.id


class TestTradingCycleResult:
    """Tests for TradingCycleResult model."""
    
    def test_trading_cycle_result_creation(self):
        """Test TradingCycleResult creation."""
        result = TradingCycleResult(
            name="test-fund",
            description="Test description",
            stocks=["NVDA", "TSLA"],
            task="Test task",
        )
        
        assert result.name == "test-fund"
        assert result.stocks == ["NVDA", "TSLA"]
        assert result.analyses == []
    
    def test_add_analysis(self):
        """Test adding analysis to results."""
        result = TradingCycleResult(name="test")
        analysis = StockAnalysis(stock="NVDA", thesis="Test thesis")
        
        result.add_analysis(analysis)
        
        assert len(result.analyses) == 1
        assert result.analyses[0].stock == "NVDA"
    
    def test_to_string(self):
        """Test converting results to string."""
        result = TradingCycleResult(name="test")
        analysis = StockAnalysis(
            stock="NVDA",
            thesis="Buy thesis",
            risk_decision="approved",
        )
        result.add_analysis(analysis)
        
        string_output = result.to_string()
        
        assert "NVDA" in string_output
        assert "Buy thesis" in string_output
        assert "approved" in string_output

