"""
AutoHedge - Main Entry Point
Simple script to launch the automated trading system.

This demonstrates the modular architecture with scalable intelligence:
- AutoHedge orchestrates all components
- Agents handle specific tasks (Director, Quant, Risk, Execution)
- Data module provides market information
- Trading module manages the cycle and state machine
- Intelligence module provides additional market insights:
  * Data Providers: Real data from Yahoo Finance (earnings, news)
  * AI Providers: LLM-powered analysis (sentiment, macro, sector)
"""
from dotenv import load_dotenv
from autohedge import AutoHedge


def main():
    """
    Main function to launch the trading system.
    
    Flow:
    1. Initialize AutoHedge with configuration
    2. Enable data providers for real market data
    3. Run trading cycle for specified stocks
    4. Display results with enriched intelligence
    """
    # Load environment variables (OPENAI_API_KEY, etc.)
    load_dotenv()
    
    # Define stocks to analyze
    stocks = ["SPY"]
    
    # Initialize the trading system with intelligence enabled
    hedge = AutoHedge(
        stocks=stocks,
        name="crew-fund",
        description="Private Hedge Fund using Crew AI with Intelligence",
        llm_model="gpt-4o-mini",
        output_type="str",
        # Enable scalable intelligence for enriched risk assessment
        enable_intelligence=True,
        # Select which providers to use:
        # - earnings: Real quarterly earnings data (Yahoo Finance)
        # - news_scraper: Real financial news (Yahoo Finance)
        # - sentiment: AI-powered sentiment analysis
        # - macro: AI-powered macroeconomic analysis
        intelligence_providers=["earnings", "news_scraper", "sentiment", "macro"],
    )
    
    # Define the trading task
    task = (
        "As BlackRock, evaluate AI companies for a portfolio with "
        "30k USD allocation, aiming for a balanced risk-reward profile."
    )
    
    # Execute trading cycle
    print("\n" + "="*80)
    print("STARTING AUTOMATED TRADING SYSTEM")
    print("="*80)
    print(f"\nIntelligence Providers: {hedge.list_intelligence_providers()}")
    print(f"  - Data Providers: earnings, news_scraper (real data from Yahoo Finance)")
    print(f"  - AI Providers: sentiment, macro (LLM-powered analysis)")
    print(f"\nStocks: {stocks}")
    print(f"LLM Model: {hedge.config.llm_model}")
    print("\n" + "="*80 + "\n")
    
    results = hedge.run(task=task)
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80 + "\n")
    print(results)


if __name__ == "__main__":
    main()
