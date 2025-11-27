"""
AutoHedge - Usage Examples

This file demonstrates various ways to use the AutoHedge trading system,
including the data providers (real data) and AI providers (LLM analysis).
"""
from dotenv import load_dotenv
from autohedge import (
    AutoHedge,
    Config,
    MarketDataProvider,
    # Intelligence components
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
)

# Load environment variables
load_dotenv()


# =============================================================================
# Example 1: Basic Usage (No Intelligence)
# =============================================================================

def basic_example():
    """Simple usage with default settings, no intelligence providers."""
    hedge = AutoHedge(
        stocks=["NVDA", "TSLA"],
        llm_model="gpt-4o-mini",
        enable_intelligence=False,
    )
    
    results = hedge.run(
        task="Analyze these tech stocks for a growth-oriented portfolio"
    )
    print(results)


# =============================================================================
# Example 2: With Data Providers Only (Real Data, No AI)
# =============================================================================

def data_providers_example():
    """Usage with real data providers (no LLM calls for intelligence)."""
    hedge = AutoHedge(
        stocks=["NVDA"],
        llm_model="gpt-4o-mini",
        enable_intelligence=True,
        # Only use data providers (faster, no extra LLM calls)
        intelligence_providers=["earnings", "news_scraper"],
    )
    
    print(f"Active providers: {hedge.list_intelligence_providers()}")
    print("These providers fetch REAL DATA from Yahoo Finance!\n")
    
    results = hedge.run(
        task="Analyze NVIDIA with real earnings and news data"
    )
    print(results)


# =============================================================================
# Example 3: Full Intelligence (Data + AI)
# =============================================================================

def full_intelligence_example():
    """Usage with both data providers and AI analysis providers."""
    hedge = AutoHedge(
        stocks=["AAPL"],
        llm_model="gpt-4o-mini",
        enable_intelligence=True,
        intelligence_providers=[
            # Data providers (real data from Yahoo Finance)
            "earnings",
            "news_scraper",
            # AI providers (LLM-powered analysis)
            "sentiment",
            "macro",
        ],
    )
    
    print(f"All providers: {hedge.list_intelligence_providers()}")
    
    results = hedge.run(
        task="Comprehensive analysis of Apple stock with all intelligence"
    )
    print(results)


# =============================================================================
# Example 4: Using Data Providers Directly
# =============================================================================

def direct_providers_example():
    """Use data providers directly to fetch real market data."""
    
    # Fetch real earnings data
    print("=" * 60)
    print("EARNINGS DATA (Real from Yahoo Finance)")
    print("=" * 60)
    
    earnings_provider = EarningsProvider()
    earnings_result = earnings_provider.analyze("NVDA")
    
    print(earnings_result.summary)
    print(f"\nConfidence: {earnings_result.confidence:.0%}")
    print(f"Risk Impact: {earnings_result.risk_impact:+.2f}")
    
    # Fetch real news
    print("\n" + "=" * 60)
    print("NEWS DATA (Real from Yahoo Finance)")
    print("=" * 60)
    
    news_provider = NewsScraperProvider(max_news=5)
    news_result = news_provider.analyze("NVDA")
    
    print(news_result.summary)
    print(f"\nConfidence: {news_result.confidence:.0%}")
    print(f"Risk Impact: {news_result.risk_impact:+.2f}")


# =============================================================================
# Example 5: Using Intelligence Registry Directly
# =============================================================================

def registry_example():
    """Direct usage of the intelligence registry with mixed providers."""
    # Create registry
    registry = IntelligenceRegistry(parallel=True)
    
    # Register data providers
    registry.register(EarningsProvider())
    registry.register(NewsScraperProvider())
    
    # Register AI providers
    registry.register(SentimentProvider(llm_model="gpt-4o-mini"))
    
    print(f"Registered providers: {registry.list_providers()}")
    
    # Gather all insights for a stock
    print("\nGathering insights for GOOGL...")
    insights = registry.gather_insights("GOOGL")
    
    for insight in insights:
        print(f"\n{'='*50}")
        print(f"Provider: {insight.provider_name}")
        print(f"Type: {insight.intelligence_type.value}")
        print(f"Confidence: {insight.confidence:.0%}")
        print(f"Risk Impact: {insight.risk_impact:+.2f}")
        print(f"Summary (first 300 chars):\n{insight.summary[:300]}...")
    
    # Get risk adjustment
    risk_adj = registry.get_risk_adjustment("GOOGL")
    print(f"\n{'='*50}")
    print(f"Aggregated Risk Adjustment: {risk_adj:+.2f}")


# =============================================================================
# Example 6: Custom Provider Example
# =============================================================================

class ESGProvider(IntelligenceProvider):
    """Custom provider for ESG (Environmental, Social, Governance) analysis."""
    
    @property
    def name(self) -> str:
        return "esg_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.CUSTOM
    
    @property
    def description(self) -> str:
        return "Analyzes ESG factors for sustainable investing"
    
    def analyze(self, stock: str, context=None) -> IntelligenceResult:
        """Perform ESG analysis (simplified example)."""
        # In real implementation, would call ESG data APIs
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=stock,
            data={
                "environmental_score": 0.75,
                "social_score": 0.80,
                "governance_score": 0.85,
            },
            summary=f"ESG analysis for {stock}: Strong governance, good social practices",
            confidence=0.7,
            risk_impact=0.1,
        )


def custom_provider_example():
    """Usage with a custom intelligence provider."""
    hedge = AutoHedge(
        stocks=["MSFT"],
        llm_model="gpt-4o-mini",
        enable_intelligence=True,
        intelligence_providers=["earnings", "news_scraper"],
    )
    
    # Add custom ESG provider
    hedge.add_intelligence_provider(ESGProvider())
    
    print(f"Providers after adding custom: {hedge.list_intelligence_providers()}")
    
    results = hedge.run(
        task="Analyze Microsoft with ESG considerations"
    )
    print(results)


# =============================================================================
# Example 7: Configuration Reference
# =============================================================================

def config_reference():
    """Show all available configuration options."""
    print("""
AutoHedge Configuration Options:
================================

Basic Configuration:
- stocks: List[str]           - Stock symbols to analyze
- name: str                   - System name (default: "autohedge")
- output_type: str            - Output format: "str", "list", "dict"
- max_retries: int            - Max retries on risk rejection (default: 3)
- llm_model: str              - LLM model to use (default: "gpt-4o-mini")

Intelligence Configuration:
- enable_intelligence: bool   - Enable intelligence system (default: False)
- intelligence_providers: List[str] - Providers to enable:

    📊 DATA PROVIDERS (Real Data from Yahoo Finance):
    - "earnings"      : Quarterly earnings, EPS, revenue, growth
    - "news_scraper"  : Real financial news headlines

    🧠 AI PROVIDERS (LLM-Powered Analysis):
    - "sentiment"     : Market sentiment from social/analysts
    - "macro"         : Macroeconomic factors
    - "sector"        : Sector dynamics and competition
    - "technical"     : Advanced technical analysis
    - "news"          : AI-powered news analysis

    None = All providers enabled

Example:
    hedge = AutoHedge(
        stocks=["NVDA"],
        llm_model="gpt-4o-mini",
        enable_intelligence=True,
        intelligence_providers=["earnings", "news_scraper", "sentiment"],
    )
""")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("="*80)
    print("AUTOHEDGE EXAMPLES")
    print("="*80)
    
    # Show configuration reference
    config_reference()
    
    # Uncomment the example you want to run:
    
    # basic_example()
    # data_providers_example()
    # full_intelligence_example()
    direct_providers_example()  # <-- Demonstrates real data fetching
    # registry_example()
    # custom_provider_example()
