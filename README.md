# AutoHedge 🚀

Automated Trading Insights System using Crew AI.

A multi-agent trading system that provides comprehensive market analysis,
quantitative insights, risk assessment, and trade recommendations with
**scalable intelligence providers** for enriched decision making.

## 📁 Project Structure

```
autohedge/
├── __init__.py              # Main exports
├── autohedge.py             # Main AutoHedge class
│
├── core/                    # Core module
│   ├── config.py            # Configuration management
│   ├── enums.py             # TradingState, RiskDecision enums
│   └── models.py            # Pydantic data models
│
├── agents/                  # AI Agents module
│   ├── factory.py           # Agent creation factory
│   └── prompts.py           # Agent role definitions
│
├── data/                    # Data module
│   └── market.py            # Market data provider (yfinance)
│
├── trading/                 # Trading module
│   ├── cycle.py             # Trading cycle orchestration
│   ├── state_machine.py     # State machine management
│   └── tasks.py             # Task factory for agents
│
└── intelligence/            # Scalable Intelligence module ⭐
    ├── base.py              # Base provider interface
    ├── registry.py          # Provider registry
    └── providers/           # Intelligence providers
        ├── earnings.py      # 📊 Real quarterly earnings (Yahoo Finance)
        ├── news_scraper.py  # 📰 Real financial news (Yahoo Finance)
        ├── sentiment.py     # 🧠 AI sentiment analysis
        ├── macro.py         # 🌍 AI macroeconomic analysis
        ├── sector.py        # 🏭 AI sector dynamics
        ├── technical.py     # 📈 AI technical analysis
        └── news.py          # 📰 AI news analysis
```

## 🏗️ Architecture

### Intelligence Provider Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligence Registry                        │
│                                                                 │
│  📊 DATA PROVIDERS              🧠 AI PROVIDERS                  │
│  (Real Data from Internet)     (LLM-Powered Analysis)          │
│  ┌──────────────────┐          ┌────────────────┐              │
│  │ EarningsProvider │          │SentimentProvider│              │
│  │ • Quarterly EPS  │          │ • Social media │              │
│  │ • Revenue        │          │ • Analyst views│              │
│  │ • Growth metrics │          └────────────────┘              │
│  └──────────────────┘          ┌────────────────┐              │
│  ┌──────────────────┐          │  MacroProvider │              │
│  │NewsScraperProvider│         │ • Interest rates│             │
│  │ • Real headlines │          │ • Inflation    │              │
│  │ • Publisher info │          │ • GDP growth   │              │
│  │ • Publish dates  │          └────────────────┘              │
│  └──────────────────┘          + more AI providers...          │
│                                                                 │
│         └────────────────────┬──────────────────────────────────┘
│                              ▼                                  │
│              ┌───────────────────────┐                          │
│              │  Aggregated Insights  │                          │
│              └───────────────────────┘                          │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │ Enhanced Risk Assessment│                         │
│              └───────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY="your-openai-api-key"
```

### Basic Usage

```python
from autohedge import AutoHedge

# Simple usage without intelligence
hedge = AutoHedge(
    stocks=["NVDA", "TSLA", "MSFT"],
    llm_model="gpt-4o-mini",
)

results = hedge.run(
    task="Analyze AI companies for a balanced portfolio"
)
print(results)
```

### With Data Providers (Real Data from Internet)

```python
from autohedge import AutoHedge

# Enable real data providers for earnings and news
hedge = AutoHedge(
    stocks=["NVDA"],
    llm_model="gpt-4o-mini",
    enable_intelligence=True,
    intelligence_providers=[
        "earnings",      # Real quarterly earnings from Yahoo Finance
        "news_scraper",  # Real financial news from Yahoo Finance
    ],
)

results = hedge.run(task="Analyze with real market data")
```

### With Full Intelligence (Data + AI Analysis)

```python
from autohedge import AutoHedge

hedge = AutoHedge(
    stocks=["NVDA"],
    llm_model="gpt-4o-mini",
    enable_intelligence=True,
    intelligence_providers=[
        # Data providers (real data)
        "earnings",
        "news_scraper",
        # AI analysis providers
        "sentiment",
        "macro",
        "sector",
    ],
)

results = hedge.run(task="Complete analysis with all intelligence")
```

### Run from Command Line

```bash
python main.py
```

## 🧠 Intelligence Providers

### 📊 Data Providers (Real Data from Internet)

| Provider | Description | Data Source |
|----------|-------------|-------------|
| `earnings` | Quarterly earnings, EPS, revenue, growth | Yahoo Finance |
| `news_scraper` | Real financial headlines and news | Yahoo Finance |

### 🤖 AI Analysis Providers (LLM-Powered)

| Provider | Description | Risk Impact |
|----------|-------------|-------------|
| `sentiment` | Market sentiment from social/analysts | ±30% |
| `macro` | Macroeconomic factors analysis | ±40% |
| `sector` | Sector dynamics and competition | ±25% |
| `technical` | Advanced technical analysis | ±20% |
| `news` | AI-powered news sentiment | ±35% |

### Data Provider Details

#### EarningsProvider 📊
```python
# Data retrieved:
- Quarterly earnings history (last 4 quarters)
- EPS (Earnings Per Share) - trailing and forward
- Revenue and revenue growth
- Profit margins (gross, operating, net)
- P/E ratio and PEG ratio
- Upcoming earnings date
- Earnings surprises (beat/miss history)
```

#### NewsScraperProvider 📰
```python
# Data retrieved:
- Recent headlines (up to 10 articles)
- Publisher information
- Publication dates
- News sentiment analysis
- Categorization (positive/negative/neutral)
- Related tickers
```

### Adding Custom Providers

```python
from autohedge import AutoHedge, IntelligenceProvider, IntelligenceResult
from autohedge.intelligence.base import IntelligenceType

class ESGProvider(IntelligenceProvider):
    @property
    def name(self) -> str:
        return "esg_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.CUSTOM
    
    def analyze(self, stock, context=None) -> IntelligenceResult:
        # Your analysis logic here
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=stock,
            summary="ESG analysis results",
            confidence=0.8,
            risk_impact=0.1,
        )

# Use custom provider
hedge = AutoHedge(stocks=["NVDA"], enable_intelligence=True)
hedge.add_intelligence_provider(ESGProvider())
```

## 🔧 Configuration Options

```python
AutoHedge(
    # Basic
    stocks=["NVDA"],           # Stock symbols to analyze
    name="my-fund",            # System name
    output_type="str",         # Output format: "str", "list", "dict"
    max_retries=3,             # Max retries on risk rejection
    llm_model="gpt-4o-mini",   # LLM model to use
    
    # Intelligence
    enable_intelligence=True,  # Enable intelligence system
    intelligence_providers=[   # Providers to enable (None = all)
        # Data providers
        "earnings",            # Real earnings data
        "news_scraper",        # Real news data
        # AI providers
        "sentiment",
        "macro",
        "sector",
        "technical",
        "news",
    ],
)
```

## 🔄 Flow Explanation

1. **Initialization**: Load configuration, create agents
2. **Data Gathering**: Fetch real earnings and news from Yahoo Finance
3. **AI Analysis**: Run AI providers for sentiment, macro, sector analysis
4. **Intelligence Aggregation**: Combine all insights
5. **Market Data**: Retrieve stock data via yfinance
6. **Thesis Generation**: Director creates thesis with intel context
7. **Quant Analysis**: Quant agent performs numerical analysis
8. **Risk Assessment**: Risk agent evaluates with all intelligence
9. **Order Generation**: Execution agent creates trade order
10. **Output**: Return formatted analysis results

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Crew AI](https://github.com/joaomdmoura/crewAI) for the agent framework
- [yfinance](https://github.com/ranaroussi/yfinance) for market data and news

---
Created by [The Swarm Corporation](https://github.com/The-Swarm-Corporation)
