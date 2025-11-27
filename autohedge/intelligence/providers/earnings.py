"""
Earnings intelligence provider.
Retrieves real quarterly earnings data from Yahoo Finance.
Handles both stocks and ETFs appropriately.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import yfinance as yf
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


# Known ETF symbols (common ones)
KNOWN_ETFS = {
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "EEM", "EFA",
    "GLD", "SLV", "USO", "UNG", "TLT", "IEF", "SHY", "LQD", "HYG", "JNK",
    "XLF", "XLK", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE",
    "VNQ", "ARKK", "ARKG", "ARKW", "ARKF", "SOXL", "TQQQ", "SQQQ", "UPRO",
    "SPXL", "SPXS", "VGT", "VHT", "VFH", "VDE", "VCR", "VDC", "VIS", "VAW",
}


class EarningsProvider(IntelligenceProvider):
    """
    Provider for quarterly earnings data and ETF metrics.
    
    For Stocks - Retrieves:
    - Quarterly earnings history
    - EPS (Earnings Per Share)
    - Revenue
    - Earnings surprises (beat/miss)
    - Year-over-year growth
    - Upcoming earnings dates
    
    For ETFs - Retrieves:
    - Total assets under management
    - Expense ratio
    - Holdings information
    - Yield/dividend info
    - Category and benchmark
    """
    
    @property
    def name(self) -> str:
        return "earnings_analyzer"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.FUNDAMENTAL
    
    @property
    def description(self) -> str:
        return "Retrieves quarterly earnings data (stocks) or fund metrics (ETFs)"
    
    def _is_etf(self, ticker, info: Dict) -> bool:
        """Check if the ticker is an ETF."""
        symbol = ticker.ticker.upper()
        
        # Check known ETFs
        if symbol in KNOWN_ETFS:
            return True
        
        # Check quoteType from info
        quote_type = info.get("quoteType", "").upper()
        if quote_type == "ETF":
            return True
        
        # Check fund family (ETFs have this)
        if info.get("fundFamily"):
            return True
        
        # Check category (ETFs typically have categories like "Large Blend")
        if info.get("category") and not info.get("sector"):
            return True
        
        return False
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Retrieve and analyze earnings data for a stock or ETF metrics."""
        logger.info(f"Fetching fundamental data for {stock}")
        
        try:
            ticker = yf.Ticker(stock)
            info = ticker.info
            
            # Check if this is an ETF
            is_etf = self._is_etf(ticker, info)
            
            if is_etf:
                return self._analyze_etf(stock, ticker, info)
            else:
                return self._analyze_stock(stock, ticker, info)
            
        except Exception as e:
            logger.error(f"Fundamental data fetch failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Failed to fetch fundamental data: {str(e)}",
                confidence=0.0,
            )
    
    def _analyze_etf(self, symbol: str, ticker, info: Dict) -> IntelligenceResult:
        """Analyze ETF-specific metrics."""
        logger.info(f"{symbol} detected as ETF - fetching ETF metrics")
        
        # Get ETF specific data
        etf_data = {
            "is_etf": True,
            "fund_name": info.get("longName", info.get("shortName", symbol)),
            "fund_family": info.get("fundFamily", "N/A"),
            "category": info.get("category", "N/A"),
            "total_assets": info.get("totalAssets"),
            "nav_price": info.get("navPrice"),
            "expense_ratio": info.get("annualReportExpenseRatio"),
            "yield": info.get("yield"),
            "ytd_return": info.get("ytdReturn"),
            "three_year_return": info.get("threeYearAverageReturn"),
            "five_year_return": info.get("fiveYearAverageReturn"),
            "beta": info.get("beta3Year"),
            "dividend_rate": info.get("dividendRate"),
            "dividend_yield": info.get("dividendYield"),
            "trailing_pe": info.get("trailingPE"),
            "holdings_count": info.get("holdings"),
        }
        
        # Generate ETF summary
        summary = self._generate_etf_summary(symbol, etf_data)
        
        # Calculate risk impact for ETF
        risk_impact = self._calculate_etf_risk_impact(etf_data)
        
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=symbol,
            data=etf_data,
            summary=summary,
            confidence=0.85,
            risk_impact=risk_impact,
        )
    
    def _analyze_stock(self, symbol: str, ticker, info: Dict) -> IntelligenceResult:
        """Analyze stock earnings data."""
        # Get earnings data
        earnings_data = self._get_earnings_data(ticker)
        financials_data = self._get_financials_data(info)
        upcoming_earnings = self._get_upcoming_earnings(ticker)
        
        # Combine all data
        data = {
            "is_etf": False,
            **earnings_data,
            **financials_data,
            "upcoming_earnings": upcoming_earnings,
        }
        
        # Generate summary
        summary = self._generate_stock_summary(symbol, data)
        
        # Calculate risk impact based on earnings performance
        risk_impact = self._calculate_stock_risk_impact(data)
        
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=symbol,
            data=data,
            summary=summary,
            confidence=0.85,
            risk_impact=risk_impact,
        )
    
    def _get_earnings_data(self, ticker) -> Dict[str, Any]:
        """Get historical earnings data."""
        try:
            # Try earnings_dates first (more reliable)
            try:
                earnings_dates = ticker.earnings_dates
                if earnings_dates is not None and not earnings_dates.empty:
                    recent = earnings_dates.head(4)
                    history = []
                    for date, row in recent.iterrows():
                        history.append({
                            "date": str(date),
                            "eps_estimate": row.get("EPS Estimate", "N/A"),
                            "reported_eps": row.get("Reported EPS", "N/A"),
                            "surprise_percent": row.get("Surprise(%)", "N/A"),
                        })
                    return {
                        "earnings_history": history,
                        "has_earnings_data": True,
                    }
            except Exception:
                pass
            
            return {"has_earnings_data": False}
            
        except Exception as e:
            logger.warning(f"Could not fetch earnings history: {e}")
            return {"has_earnings_data": False, "error": str(e)}
    
    def _get_financials_data(self, info: Dict) -> Dict[str, Any]:
        """Get financial data from info."""
        financials = {
            # Profitability
            "profit_margins": info.get("profitMargins"),
            "operating_margins": info.get("operatingMargins"),
            "gross_margins": info.get("grossMargins"),
            
            # Growth
            "earnings_growth": info.get("earningsGrowth"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
            
            # Valuation
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            
            # Revenue & Earnings
            "total_revenue": info.get("totalRevenue"),
            "revenue_per_share": info.get("revenuePerShare"),
            "trailing_eps": info.get("trailingEps"),
            "forward_eps": info.get("forwardEps"),
            
            # Cash Flow
            "free_cash_flow": info.get("freeCashflow"),
            "operating_cash_flow": info.get("operatingCashflow"),
        }
        
        return {"financials": financials}
    
    def _get_upcoming_earnings(self, ticker) -> Dict[str, Any]:
        """Get upcoming earnings date."""
        try:
            calendar = ticker.calendar
            
            if calendar is not None:
                if isinstance(calendar, dict):
                    return {
                        "earnings_date": str(calendar.get("Earnings Date", ["N/A"])),
                        "ex_dividend_date": str(calendar.get("Ex-Dividend Date", "N/A")),
                        "dividend_date": str(calendar.get("Dividend Date", "N/A")),
                    }
            
            return {"earnings_date": "N/A"}
            
        except Exception as e:
            logger.warning(f"Could not fetch upcoming earnings: {e}")
            return {"earnings_date": "N/A"}
    
    def _generate_etf_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Generate human-readable summary for ETF."""
        lines = [f"📊 ETF FUND DATA FOR {symbol}", "=" * 50]
        
        lines.append(f"\n🏦 {data.get('fund_name', symbol)}")
        
        if data.get("fund_family"):
            lines.append(f"   Fund Family: {data['fund_family']}")
        if data.get("category"):
            lines.append(f"   Category: {data['category']}")
        
        lines.append("\n📈 KEY METRICS:")
        
        if data.get("total_assets"):
            assets_b = data["total_assets"] / 1e9
            lines.append(f"  • Total Assets: ${assets_b:.2f}B")
        
        if data.get("expense_ratio"):
            lines.append(f"  • Expense Ratio: {data['expense_ratio']*100:.2f}%")
        
        if data.get("trailing_pe"):
            lines.append(f"  • P/E Ratio: {data['trailing_pe']:.2f}")
        
        if data.get("dividend_yield"):
            lines.append(f"  • Dividend Yield: {data['dividend_yield']*100:.2f}%")
        
        if data.get("beta"):
            lines.append(f"  • Beta (3Y): {data['beta']:.2f}")
        
        lines.append("\n📊 PERFORMANCE:")
        
        if data.get("ytd_return"):
            lines.append(f"  • YTD Return: {data['ytd_return']*100:.1f}%")
        
        if data.get("three_year_return"):
            lines.append(f"  • 3-Year Avg Return: {data['three_year_return']*100:.1f}%")
        
        if data.get("five_year_return"):
            lines.append(f"  • 5-Year Avg Return: {data['five_year_return']*100:.1f}%")
        
        return "\n".join(lines)
    
    def _generate_stock_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Generate human-readable summary for stock."""
        lines = [f"📊 QUARTERLY EARNINGS DATA FOR {symbol}", "=" * 50]
        
        # Financials
        financials = data.get("financials", {})
        if financials:
            lines.append("\n📈 KEY FINANCIAL METRICS:")
            
            if financials.get("trailing_eps"):
                lines.append(f"  • Trailing EPS: ${financials['trailing_eps']:.2f}")
            if financials.get("forward_eps"):
                lines.append(f"  • Forward EPS: ${financials['forward_eps']:.2f}")
            if financials.get("trailing_pe"):
                lines.append(f"  • P/E Ratio: {financials['trailing_pe']:.2f}")
            if financials.get("earnings_growth"):
                lines.append(f"  • Earnings Growth: {financials['earnings_growth']*100:.1f}%")
            if financials.get("revenue_growth"):
                lines.append(f"  • Revenue Growth: {financials['revenue_growth']*100:.1f}%")
            if financials.get("profit_margins"):
                lines.append(f"  • Profit Margin: {financials['profit_margins']*100:.1f}%")
            if financials.get("total_revenue"):
                lines.append(f"  • Total Revenue: ${financials['total_revenue']:,.0f}")
        
        # Earnings History
        if data.get("earnings_history"):
            lines.append("\n📅 RECENT EARNINGS:")
            for earning in data["earnings_history"][:4]:
                date = earning.get("date", "N/A")
                eps_est = earning.get("eps_estimate", "N/A")
                reported = earning.get("reported_eps", "N/A")
                surprise = earning.get("surprise_percent", "N/A")
                
                if surprise != "N/A" and isinstance(surprise, (int, float)):
                    emoji = "✅" if surprise > 0 else "❌"
                    lines.append(f"  {emoji} {date}: EPS ${reported} (Est: ${eps_est}, Surprise: {surprise:.1f}%)")
                else:
                    lines.append(f"  • {date}: EPS ${reported} (Est: ${eps_est})")
        
        # Upcoming
        upcoming = data.get("upcoming_earnings", {})
        if upcoming.get("earnings_date") and upcoming["earnings_date"] != "N/A":
            lines.append(f"\n📆 NEXT EARNINGS: {upcoming['earnings_date']}")
        
        return "\n".join(lines)
    
    def _calculate_etf_risk_impact(self, data: Dict[str, Any]) -> float:
        """Calculate risk impact for ETF."""
        risk_score = 0.0
        factors = 0
        
        # Beta impact (beta < 1 = less risky)
        beta = data.get("beta")
        if beta is not None:
            if beta < 0.8:
                risk_score += 0.2  # Low volatility
            elif beta < 1.2:
                risk_score += 0.1  # Normal
            else:
                risk_score -= 0.1  # High volatility
            factors += 1
        
        # Expense ratio (lower is better)
        expense = data.get("expense_ratio")
        if expense is not None:
            if expense < 0.002:  # < 0.2%
                risk_score += 0.1
            elif expense > 0.01:  # > 1%
                risk_score -= 0.1
            factors += 1
        
        # Total assets (larger = more stable)
        assets = data.get("total_assets")
        if assets is not None:
            if assets > 10e9:  # > $10B
                risk_score += 0.1
            elif assets < 100e6:  # < $100M
                risk_score -= 0.1
            factors += 1
        
        # YTD return
        ytd = data.get("ytd_return")
        if ytd is not None:
            if ytd > 0.1:
                risk_score += 0.1
            elif ytd < -0.1:
                risk_score -= 0.1
            factors += 1
        
        if factors == 0:
            return 0.0
        
        return max(-1.0, min(1.0, risk_score / factors))
    
    def _calculate_stock_risk_impact(self, data: Dict[str, Any]) -> float:
        """Calculate risk impact for stock."""
        risk_score = 0.0
        factors = 0
        
        financials = data.get("financials", {})
        
        # Earnings growth impact
        earnings_growth = financials.get("earnings_growth")
        if earnings_growth is not None:
            if earnings_growth > 0.2:
                risk_score += 0.3
            elif earnings_growth > 0:
                risk_score += 0.1
            elif earnings_growth > -0.1:
                risk_score -= 0.1
            else:
                risk_score -= 0.3
            factors += 1
        
        # Profit margin impact
        profit_margins = financials.get("profit_margins")
        if profit_margins is not None:
            if profit_margins > 0.2:
                risk_score += 0.2
            elif profit_margins > 0.1:
                risk_score += 0.1
            elif profit_margins > 0:
                risk_score += 0.0
            else:
                risk_score -= 0.2
            factors += 1
        
        # P/E ratio sanity check
        pe_ratio = financials.get("trailing_pe")
        if pe_ratio is not None:
            if 10 < pe_ratio < 30:
                risk_score += 0.1
            elif pe_ratio > 100:
                risk_score -= 0.2
            factors += 1
        
        if factors == 0:
            return 0.0
        
        return max(-1.0, min(1.0, risk_score / factors))
