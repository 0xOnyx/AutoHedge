"""
Data models for the trading system.
Defines Pydantic models for structured data handling.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MarketData(BaseModel):
    """
    Market data model containing raw and formatted market information.
    
    Data Flow:
    Input Layer -> Market Data -> Technical Indicators + Fundamental Data
    """
    stock: str
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[float] = None
    pe_ratio: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    volatility: Optional[float] = None
    variation_1m: Optional[float] = None
    formatted: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def raw(self) -> Dict[str, Any]:
        """Return raw market data as dictionary."""
        return {
            "current_price": self.current_price,
            "market_cap": self.market_cap,
            "volume": self.volume,
            "pe_ratio": self.pe_ratio,
            "technical_indicators": {
                "sma_20": self.sma_20,
                "sma_50": self.sma_50,
                "volatility": self.volatility,
                "variation_1m": self.variation_1m,
            }
        }


class StockAnalysis(BaseModel):
    """
    Output model for individual stock analysis.
    Contains all analysis results for a single stock.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    stock: str
    thesis: Optional[str] = None
    quant_analysis: Optional[str] = None
    risk_assessment: Optional[str] = None
    risk_decision: Optional[str] = None
    order: Optional[str] = None
    decision: Optional[str] = None
    state: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TradingCycleResult(BaseModel):
    """
    Main output model containing all analysis results for a trading cycle.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    stocks: Optional[List[str]] = None
    task: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    analyses: List[StockAnalysis] = Field(default_factory=list)
    
    def add_analysis(self, analysis: StockAnalysis) -> None:
        """Add a stock analysis to the results."""
        self.analyses.append(analysis)
    
    def to_string(self) -> str:
        """Convert results to formatted string."""
        results = []
        for analysis in self.analyses:
            result = f"""
{'='*80}
RESULT FOR {analysis.stock}
{'='*80}

THESIS:
{analysis.thesis or 'N/A'}

{'='*80}

QUANTITATIVE ANALYSIS:
{analysis.quant_analysis or 'N/A'}

{'='*80}

RISK ASSESSMENT:
{analysis.risk_assessment or 'N/A'}
Risk Decision: {analysis.risk_decision or 'N/A'}

{'='*80}

PROPOSED ORDER:
{analysis.order or 'N/A'}

{'='*80}

FINAL DECISION:
{analysis.decision or 'N/A'}

{'='*80}
"""
            results.append(result)
        return "\n\n".join(results)


