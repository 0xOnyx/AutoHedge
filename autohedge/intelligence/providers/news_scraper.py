"""
News scraper intelligence provider.
Retrieves real financial news from multiple sources.
Handles both stocks and ETFs (with category-based news).
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf
from loguru import logger

from autohedge.intelligence.base import (
    IntelligenceProvider,
    IntelligenceResult,
    IntelligenceType,
)


# ETF category to relevant keywords mapping
ETF_CATEGORY_KEYWORDS = {
    # Equity - US
    "Large Blend": ["S&P 500", "large cap", "US stocks", "stock market"],
    "Large Growth": ["growth stocks", "tech stocks", "NASDAQ", "large cap growth"],
    "Large Value": ["value stocks", "dividend", "large cap value"],
    "Mid-Cap Blend": ["mid cap", "Russell Midcap"],
    "Mid-Cap Growth": ["mid cap growth"],
    "Mid-Cap Value": ["mid cap value"],
    "Small Blend": ["small cap", "Russell 2000", "small stocks"],
    "Small Growth": ["small cap growth"],
    "Small Value": ["small cap value"],
    
    # Sector
    "Technology": ["tech stocks", "technology sector", "semiconductor", "AI stocks"],
    "Financial": ["financial stocks", "banking", "finance sector"],
    "Healthcare": ["healthcare stocks", "biotech", "pharma"],
    "Energy": ["energy stocks", "oil", "gas", "energy sector"],
    "Consumer Cyclical": ["consumer stocks", "retail", "consumer spending"],
    "Consumer Defensive": ["consumer staples", "defensive stocks"],
    "Industrials": ["industrial stocks", "manufacturing"],
    "Real Estate": ["real estate", "REITs", "property"],
    "Utilities": ["utilities stocks", "utility sector"],
    "Communications": ["communications", "telecom", "media stocks"],
    "Basic Materials": ["materials", "commodities", "mining"],
    
    # International
    "Foreign Large Blend": ["international stocks", "global markets", "foreign equities"],
    "Diversified Emerging Mkts": ["emerging markets", "EM stocks", "developing markets"],
    "Europe Stock": ["European stocks", "Europe market"],
    "China Region": ["China stocks", "Chinese market", "Asia"],
    "Japan Stock": ["Japan stocks", "Japanese market", "Nikkei"],
    
    # Fixed Income
    "Intermediate Core Bond": ["bonds", "fixed income", "Treasury"],
    "Short-Term Bond": ["short term bonds", "Treasury bills"],
    "Long-Term Bond": ["long term bonds", "Treasury bonds"],
    "High Yield Bond": ["high yield", "junk bonds", "corporate bonds"],
    "Inflation-Protected Bond": ["TIPS", "inflation bonds"],
    
    # Commodities
    "Commodities Broad Basket": ["commodities", "raw materials"],
    "Precious Metals": ["gold", "silver", "precious metals"],
    "Energy Limited Partnership": ["oil", "natural gas", "energy"],
}

# Known ETF top holdings to search for related news
ETF_TOP_HOLDINGS = {
    "SPY": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK.B", "JPM"],
    "QQQ": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA"],
    "DIA": ["UNH", "GS", "MSFT", "HD", "CAT", "AMGN", "MCD", "V"],
    "IWM": ["SMCI", "MSTR", "FTAI", "INSM", "SFM", "ANF", "FN", "TGTX"],
    "VOO": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK.B", "JPM"],
    "VTI": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK.B", "JPM"],
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "AMD", "ADBE"],
    "XLF": ["BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "SPGI"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO"],
    "XLV": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "TMO", "ABT", "PFE"],
    "ARKK": ["TSLA", "COIN", "ROKU", "SQ", "PATH", "HOOD", "RBLX", "PLTR"],
}


class NewsScraperProvider(IntelligenceProvider):
    """
    Provider for real financial news scraping.
    
    For Stocks - Retrieves:
    - Company-specific news headlines
    - Publisher and date information
    - Sentiment analysis
    
    For ETFs - Retrieves:
    - ETF-specific news
    - Category-related market news
    - Top holdings news
    - Sector/market trends
    """
    
    def __init__(self, llm_model: Optional[str] = None, max_news: int = 10):
        """
        Initialize the news scraper provider.
        
        Args:
            llm_model: Optional LLM model for sentiment analysis
            max_news: Maximum number of news items to retrieve
        """
        super().__init__(llm_model)
        self.max_news = max_news
    
    @property
    def name(self) -> str:
        return "news_scraper"
    
    @property
    def intelligence_type(self) -> IntelligenceType:
        return IntelligenceType.NEWS
    
    @property
    def description(self) -> str:
        return "Scrapes real financial news for stocks and ETFs (with category analysis)"
    
    def _is_etf(self, info: Dict) -> bool:
        """Check if the ticker is an ETF."""
        quote_type = info.get("quoteType", "").upper()
        if quote_type == "ETF":
            return True
        if info.get("fundFamily"):
            return True
        if info.get("category") and not info.get("sector"):
            return True
        return False
    
    def analyze(self, stock: str, context: Optional[Dict[str, Any]] = None) -> IntelligenceResult:
        """Retrieve and analyze news for a stock or ETF."""
        logger.info(f"Scraping news for {stock}")
        
        try:
            ticker = yf.Ticker(stock)
            info = ticker.info
            
            is_etf = self._is_etf(info)
            
            if is_etf:
                return self._analyze_etf_news(stock, ticker, info)
            else:
                return self._analyze_stock_news(stock, ticker, info)
            
        except Exception as e:
            logger.error(f"News scraping failed for {stock}: {str(e)}")
            return IntelligenceResult(
                provider_name=self.name,
                intelligence_type=self.intelligence_type,
                stock=stock,
                summary=f"Failed to scrape news: {str(e)}",
                confidence=0.0,
            )
    
    def _analyze_etf_news(self, symbol: str, ticker, info: Dict) -> IntelligenceResult:
        """Analyze news for an ETF based on category and holdings."""
        logger.info(f"{symbol} detected as ETF - fetching category-based news")
        
        # Get ETF info
        fund_name = info.get("longName", info.get("shortName", symbol))
        category = info.get("category", "Unknown")
        
        # Get ETF's own news
        etf_news = self._get_yahoo_news(ticker)
        
        # Get news for top holdings
        holdings_news = []
        top_holdings = ETF_TOP_HOLDINGS.get(symbol.upper(), [])
        
        if top_holdings:
            # Get news for top 3 holdings
            for holding in top_holdings[:3]:
                try:
                    holding_ticker = yf.Ticker(holding)
                    holding_news = self._get_yahoo_news(holding_ticker, max_items=2)
                    for item in holding_news:
                        item["related_to"] = holding
                    holdings_news.extend(holding_news)
                except Exception as e:
                    logger.warning(f"Could not fetch news for holding {holding}: {e}")
        
        # Combine all news
        all_news = etf_news + holdings_news
        
        # Get category keywords
        category_keywords = ETF_CATEGORY_KEYWORDS.get(category, [])
        
        # Analyze sentiment
        sentiment_analysis = self._analyze_sentiment(all_news)
        
        # Compile data
        data = {
            "is_etf": True,
            "fund_name": fund_name,
            "category": category,
            "category_keywords": category_keywords,
            "top_holdings_analyzed": top_holdings[:3] if top_holdings else [],
            "etf_news_count": len(etf_news),
            "holdings_news_count": len(holdings_news),
            "total_news_count": len(all_news),
            "news_items": all_news[:self.max_news],
            "sentiment": sentiment_analysis,
        }
        
        # Generate summary
        summary = self._generate_etf_news_summary(symbol, data)
        
        # Calculate risk impact
        risk_impact = self._calculate_risk_impact(sentiment_analysis)
        
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=symbol,
            data=data,
            summary=summary,
            confidence=0.75,
            risk_impact=risk_impact,
        )
    
    def _analyze_stock_news(self, symbol: str, ticker, info: Dict) -> IntelligenceResult:
        """Analyze news for a regular stock."""
        # Get company info
        company_info = {
            "name": info.get("longName", info.get("shortName", symbol)),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
        }
        
        # Get news from Yahoo Finance
        news_items = self._get_yahoo_news(ticker)
        
        # Analyze sentiment
        sentiment_analysis = self._analyze_sentiment(news_items)
        
        # Compile data
        data = {
            "is_etf": False,
            "company": company_info,
            "news_count": len(news_items),
            "news_items": news_items,
            "sentiment": sentiment_analysis,
        }
        
        # Generate summary
        summary = self._generate_stock_news_summary(symbol, data)
        
        # Calculate risk impact
        risk_impact = self._calculate_risk_impact(sentiment_analysis)
        
        return IntelligenceResult(
            provider_name=self.name,
            intelligence_type=self.intelligence_type,
            stock=symbol,
            data=data,
            summary=summary,
            confidence=0.75,
            risk_impact=risk_impact,
        )
    
    def _get_yahoo_news(self, ticker, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get news from Yahoo Finance."""
        max_items = max_items or self.max_news
        
        try:
            news = ticker.news
            
            if not news:
                return []
            
            news_items = []
            for item in news[:max_items]:
                try:
                    if item is None:
                        continue
                    
                    # Handle new yfinance format (nested in 'content')
                    if "content" in item and item.get("content") is not None:
                        content = item["content"]
                        if content is None:
                            continue
                        
                        title = content.get("title") or "No title"
                        
                        # Parse publication date
                        pub_date_str = content.get("pubDate") or content.get("displayTime")
                        if pub_date_str:
                            try:
                                publish_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                                time_ago = self._time_ago(publish_date)
                            except Exception:
                                publish_date = None
                                time_ago = "Unknown"
                        else:
                            publish_date = None
                            time_ago = "Unknown"
                        
                        # Get publisher from nested provider (with safe access)
                        provider = content.get("provider") or {}
                        publisher = provider.get("displayName") or "Unknown" if isinstance(provider, dict) else "Unknown"
                        
                        # Get link (with safe access)
                        click_url = content.get("clickThroughUrl") or {}
                        link = click_url.get("url") or "" if isinstance(click_url, dict) else ""
                        
                        news_item = {
                            "title": title,
                            "publisher": publisher,
                            "link": link,
                            "publish_date": str(publish_date) if publish_date else "Unknown",
                            "time_ago": time_ago,
                            "type": content.get("contentType") or "article",
                            "summary": content.get("summary") or "",
                            "related_tickers": [],
                        }
                    else:
                        # Handle old yfinance format (fallback)
                        publish_time = item.get("providerPublishTime", 0) if isinstance(item, dict) else 0
                        if publish_time:
                            publish_date = datetime.fromtimestamp(publish_time)
                            time_ago = self._time_ago(publish_date)
                        else:
                            publish_date = None
                            time_ago = "Unknown"
                        
                        news_item = {
                            "title": item.get("title") or "No title" if isinstance(item, dict) else "No title",
                            "publisher": item.get("publisher") or "Unknown" if isinstance(item, dict) else "Unknown",
                            "link": item.get("link") or "" if isinstance(item, dict) else "",
                            "publish_date": str(publish_date) if publish_date else "Unknown",
                            "time_ago": time_ago,
                            "type": item.get("type") or "article" if isinstance(item, dict) else "article",
                            "summary": "",
                            "related_tickers": item.get("relatedTickers") or [] if isinstance(item, dict) else [],
                        }
                    
                    # Only add if we have a valid title
                    if news_item["title"] and news_item["title"] != "No title":
                        news_items.append(news_item)
                        
                except Exception as item_error:
                    logger.debug(f"Skipping news item due to error: {item_error}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.warning(f"Could not fetch Yahoo news: {e}")
            return []
    
    def _analyze_sentiment(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news headlines."""
        if not news_items:
            return {"overall": "neutral", "score": 0.0, "breakdown": {}}
        
        positive_words = [
            "surge", "soar", "jump", "gain", "rise", "beat", "exceed", "record",
            "upgrade", "buy", "bullish", "growth", "profit", "success", "breakthrough",
            "innovation", "strong", "positive", "outperform", "rally", "boom", "high"
        ]
        
        negative_words = [
            "fall", "drop", "decline", "plunge", "crash", "miss", "cut", "downgrade",
            "sell", "bearish", "loss", "fail", "concern", "warning", "weak", "negative",
            "underperform", "slump", "trouble", "risk", "lawsuit", "investigation", "low"
        ]
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        categorized_news = {
            "positive": [],
            "negative": [],
            "neutral": [],
        }
        
        for item in news_items:
            title_lower = item["title"].lower()
            
            pos_matches = sum(1 for word in positive_words if word in title_lower)
            neg_matches = sum(1 for word in negative_words if word in title_lower)
            
            if pos_matches > neg_matches:
                positive_count += 1
                categorized_news["positive"].append(item["title"])
            elif neg_matches > pos_matches:
                negative_count += 1
                categorized_news["negative"].append(item["title"])
            else:
                neutral_count += 1
                categorized_news["neutral"].append(item["title"])
        
        total = len(news_items)
        score = (positive_count - negative_count) / total if total > 0 else 0.0
        
        if score > 0.2:
            overall = "positive"
        elif score < -0.2:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall": overall,
            "score": score,
            "breakdown": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
            },
            "categorized": categorized_news,
        }
    
    def _time_ago(self, publish_date: datetime) -> str:
        """Calculate human-readable time ago."""
        now = datetime.now()
        diff = now - publish_date
        
        if diff.days > 30:
            return f"{diff.days // 30} months ago"
        elif diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    
    def _generate_etf_news_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Generate summary for ETF news."""
        lines = [f"NEWS ANALYSIS FOR ETF {symbol}", "=" * 50]
        
        # ETF info
        lines.append(f"\n{data.get('fund_name', symbol)}")
        lines.append(f"   Category: {data.get('category', 'Unknown')}")
        
        # Category keywords
        keywords = data.get("category_keywords", [])
        if keywords:
            lines.append(f"   Related Topics: {', '.join(keywords[:4])}")
        
        # Holdings analyzed
        holdings = data.get("top_holdings_analyzed", [])
        if holdings:
            lines.append(f"   Top Holdings Analyzed: {', '.join(holdings)}")
        
        # Sentiment
        sentiment = data.get("sentiment", {})
        if sentiment:
            emoji_map = {"positive": "[+]", "negative": "[-]", "neutral": "[=]"}
            emoji = emoji_map.get(sentiment.get("overall", "neutral"), "[=]")
            
            lines.append(f"\n{emoji} NEWS SENTIMENT: {sentiment.get('overall', 'neutral').upper()}")
            lines.append(f"   Score: {sentiment.get('score', 0):.2f} (-1 to 1)")
            
            breakdown = sentiment.get("breakdown", {})
            lines.append(f"   Positive: {breakdown.get('positive', 0)} | " +
                        f"Negative: {breakdown.get('negative', 0)} | " +
                        f"Neutral: {breakdown.get('neutral', 0)}")
        
        # News counts
        lines.append(f"\n   ETF News: {data.get('etf_news_count', 0)}")
        lines.append(f"   Holdings News: {data.get('holdings_news_count', 0)}")
        
        # Headlines
        news_items = data.get("news_items", [])
        if news_items:
            lines.append(f"\nRECENT HEADLINES ({len(news_items)} articles):")
            
            for item in news_items[:7]:
                time_ago = item.get("time_ago", "")
                title = item.get("title", "")[:70]
                related = item.get("related_to", "")
                
                # Sentiment indicator
                title_lower = title.lower()
                if any(w in title_lower for w in ["surge", "beat", "gain", "rise", "record", "high"]):
                    indicator = "[+]"
                elif any(w in title_lower for w in ["fall", "drop", "miss", "cut", "decline", "low"]):
                    indicator = "[-]"
                else:
                    indicator = "[.]"
                
                if related:
                    lines.append(f"   {indicator} [{time_ago}] ({related}) {title}")
                else:
                    lines.append(f"   {indicator} [{time_ago}] {title}")
        else:
            lines.append("\n[!] No recent news found")
        
        return "\n".join(lines)
    
    def _generate_stock_news_summary(self, symbol: str, data: Dict[str, Any]) -> str:
        """Generate summary for stock news."""
        lines = [f"NEWS ANALYSIS FOR {symbol}", "=" * 50]
        
        # Company info
        company = data.get("company", {})
        if company.get("name"):
            lines.append(f"\n{company['name']}")
            if company.get("sector"):
                lines.append(f"   Sector: {company['sector']} | Industry: {company.get('industry', 'N/A')}")
        
        # Sentiment
        sentiment = data.get("sentiment", {})
        if sentiment:
            emoji_map = {"positive": "[+]", "negative": "[-]", "neutral": "[=]"}
            emoji = emoji_map.get(sentiment.get("overall", "neutral"), "[=]")
            
            lines.append(f"\n{emoji} NEWS SENTIMENT: {sentiment.get('overall', 'neutral').upper()}")
            lines.append(f"   Score: {sentiment.get('score', 0):.2f} (-1 to 1)")
            
            breakdown = sentiment.get("breakdown", {})
            lines.append(f"   Positive: {breakdown.get('positive', 0)} | " +
                        f"Negative: {breakdown.get('negative', 0)} | " +
                        f"Neutral: {breakdown.get('neutral', 0)}")
        
        # Headlines
        news_items = data.get("news_items", [])
        if news_items:
            lines.append(f"\nRECENT HEADLINES ({len(news_items)} articles):")
            
            for item in news_items[:7]:
                time_ago = item.get("time_ago", "")
                publisher = item.get("publisher", "")
                title = item.get("title", "")[:70]
                
                title_lower = title.lower()
                if any(w in title_lower for w in ["surge", "beat", "gain", "rise", "record"]):
                    indicator = "[+]"
                elif any(w in title_lower for w in ["fall", "drop", "miss", "cut", "decline"]):
                    indicator = "[-]"
                else:
                    indicator = "[.]"
                
                lines.append(f"   {indicator} [{time_ago}] {title}")
                lines.append(f"      Source: {publisher}")
        else:
            lines.append("\n[!] No recent news found")
        
        return "\n".join(lines)
    
    def _calculate_risk_impact(self, sentiment: Dict[str, Any]) -> float:
        """Calculate risk impact from news sentiment."""
        score = sentiment.get("score", 0.0)
        return score * 0.35
