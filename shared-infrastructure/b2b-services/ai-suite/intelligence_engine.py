"""
GridWorks AI Suite - Intelligence Engine
Global market correlation analysis, pre-market intelligence, and institutional flow tracking
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import redis
import json
from dataclasses import dataclass
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor

from ..database.models import EnterpriseClient, UsageRecord
from ..database.session import get_db
from ..config import settings
from ..utils.market_data import MarketDataProvider
from ..utils.correlation_analyzer import CorrelationAnalyzer
from ..utils.notifications import send_notification


class IntelligenceType(str, Enum):
    """Types of intelligence services"""
    MORNING_PULSE = "morning_pulse"
    CORRELATION_ANALYSIS = "correlation_analysis"
    INSTITUTIONAL_FLOW = "institutional_flow"
    MARKET_SENTIMENT = "market_sentiment"
    RISK_ALERTS = "risk_alerts"
    OPPORTUNITY_SCANNER = "opportunity_scanner"


class DeliveryFormat(str, Enum):
    """Intelligence delivery formats"""
    JSON = "json"
    PDF_REPORT = "pdf_report"
    AUDIO_BRIEFING = "audio_briefing"
    EMAIL_DIGEST = "email_digest"
    WHATSAPP_SUMMARY = "whatsapp_summary"
    API_WEBHOOK = "api_webhook"


class MarketRegion(str, Enum):
    """Market regions for analysis"""
    GLOBAL = "global"
    INDIA = "india"
    US = "us"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"


@dataclass
class IntelligenceRequest:
    """Intelligence request structure"""
    client_id: str
    intelligence_type: IntelligenceType
    market_regions: List[MarketRegion]
    delivery_format: DeliveryFormat
    custom_parameters: Dict[str, Any]
    delivery_time: Optional[datetime] = None
    webhook_url: Optional[str] = None


@dataclass
class MarketIntelligence:
    """Market intelligence data structure"""
    timestamp: datetime
    intelligence_type: IntelligenceType
    market_region: MarketRegion
    summary: str
    key_insights: List[str]
    data_points: Dict[str, Any]
    confidence_score: float
    risk_level: str
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any]


class GlobalCorrelationEngine:
    """
    Analyzes correlations between global markets and Indian markets
    NASDAQ → Indian markets intelligence
    """
    
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Key market indices for correlation analysis
        self.key_indices = {
            "global": {
                "nasdaq": "^IXIC",
                "sp500": "^GSPC",
                "dow": "^DJI",
                "ftse": "^FTSE",
                "nikkei": "^N225",
                "hang_seng": "^HSI"
            },
            "india": {
                "nifty_50": "^NSEI",
                "sensex": "^BSESN",
                "bank_nifty": "NIFTY_BANK.NS",
                "nifty_it": "NIFTY_IT.NS",
                "nifty_pharma": "NIFTY_PHARMA.NS"
            }
        }
    
    async def analyze_global_correlations(
        self,
        timeframe: str = "30d",
        update_cache: bool = False
    ) -> Dict[str, Any]:
        """Analyze correlations between global and Indian markets"""
        
        cache_key = f"global_correlations:{timeframe}"
        
        if not update_cache:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
        # Fetch market data for all indices
        market_data = {}
        
        for region, indices in self.key_indices.items():
            market_data[region] = {}
            for name, symbol in indices.items():
                try:
                    data = await self.market_data.get_historical_data(
                        symbol, timeframe
                    )
                    market_data[region][name] = data
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
        
        # Calculate correlations
        correlations = {}
        
        for global_market, global_data in market_data["global"].items():
            correlations[global_market] = {}
            
            for indian_market, indian_data in market_data["india"].items():
                correlation = self.correlation_analyzer.calculate_correlation(
                    global_data, indian_data
                )
                correlations[global_market][indian_market] = {
                    "correlation": correlation,
                    "strength": self._interpret_correlation_strength(correlation),
                    "significance": self._calculate_significance(global_data, indian_data)
                }
        
        # Identify strongest correlations
        strongest_correlations = self._find_strongest_correlations(correlations)
        
        # Generate insights
        insights = self._generate_correlation_insights(correlations, strongest_correlations)
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "timeframe": timeframe,
            "correlations": correlations,
            "strongest_correlations": strongest_correlations,
            "insights": insights,
            "market_status": await self._get_market_status()
        }
        
        # Cache for 1 hour
        self.redis_client.setex(cache_key, 3600, json.dumps(result, default=str))
        
        return result
    
    def _interpret_correlation_strength(self, correlation: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "very_strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _calculate_significance(self, data1: pd.DataFrame, data2: pd.DataFrame) -> float:
        """Calculate statistical significance of correlation"""
        # Simplified p-value calculation
        # In production, use proper statistical tests
        n = min(len(data1), len(data2))
        if n < 30:
            return 0.5  # Not enough data
        return 0.05 if n > 100 else 0.1  # Simplified
    
    def _find_strongest_correlations(self, correlations: Dict) -> List[Dict]:
        """Find and rank strongest correlations"""
        strongest = []
        
        for global_market in correlations:
            for indian_market in correlations[global_market]:
                corr_data = correlations[global_market][indian_market]
                strongest.append({
                    "global_market": global_market,
                    "indian_market": indian_market,
                    "correlation": corr_data["correlation"],
                    "strength": corr_data["strength"],
                    "significance": corr_data["significance"]
                })
        
        # Sort by absolute correlation value
        strongest.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        return strongest[:10]  # Top 10
    
    def _generate_correlation_insights(
        self,
        correlations: Dict,
        strongest: List[Dict]
    ) -> List[str]:
        """Generate actionable insights from correlation analysis"""
        insights = []
        
        # Strongest positive correlation
        if strongest and strongest[0]["correlation"] > 0.7:
            insights.append(
                f"Strong positive correlation detected: {strongest[0]['global_market']} "
                f"and {strongest[0]['indian_market']} ({strongest[0]['correlation']:.3f}). "
                f"Consider monitoring {strongest[0]['global_market']} for early signals."
            )
        
        # Look for sector-specific patterns
        nasdaq_it_corr = correlations.get("nasdaq", {}).get("nifty_it", {}).get("correlation", 0)
        if nasdaq_it_corr > 0.6:
            insights.append(
                f"NASDAQ shows strong correlation with Nifty IT ({nasdaq_it_corr:.3f}). "
                "US tech earnings could significantly impact Indian IT stocks."
            )
        
        # Check for divergences
        sp500_nifty_corr = correlations.get("sp500", {}).get("nifty_50", {}).get("correlation", 0)
        if abs(sp500_nifty_corr) < 0.3:
            insights.append(
                "Low correlation between S&P 500 and Nifty 50 suggests potential "
                "independent movement patterns. Local factors may dominate."
            )
        
        return insights
    
    async def _get_market_status(self) -> Dict[str, Any]:
        """Get current market status across regions"""
        now = datetime.utcnow()
        
        return {
            "us_market": self._is_market_open(now, "US"),
            "indian_market": self._is_market_open(now, "India"),
            "european_market": self._is_market_open(now, "Europe"),
            "asian_market": self._is_market_open(now, "Asia")
        }
    
    def _is_market_open(self, timestamp: datetime, region: str) -> Dict[str, Any]:
        """Check if market is open for a region"""
        # Simplified market hours (adjust for actual trading hours and holidays)
        market_hours = {
            "US": {"open": time(14, 30), "close": time(21, 0)},  # EST in UTC
            "India": {"open": time(3, 45), "close": time(10, 0)},  # IST in UTC
            "Europe": {"open": time(8, 0), "close": time(16, 30)},  # GMT in UTC
            "Asia": {"open": time(0, 0), "close": time(7, 0)}  # JST in UTC
        }
        
        current_time = timestamp.time()
        hours = market_hours.get(region, {"open": time(0, 0), "close": time(23, 59)})
        
        is_open = hours["open"] <= current_time <= hours["close"]
        
        return {
            "is_open": is_open,
            "open_time": hours["open"].strftime("%H:%M"),
            "close_time": hours["close"].strftime("%H:%M"),
            "current_time": current_time.strftime("%H:%M")
        }


class MorningPulseGenerator:
    """
    Generates morning market pulse with pre-market intelligence
    Delivered at 7:30 AM IST daily
    """
    
    def __init__(self):
        self.correlation_engine = GlobalCorrelationEngine()
        self.market_data = MarketDataProvider()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def generate_morning_pulse(
        self,
        client_id: str,
        custom_focus: List[str] = None
    ) -> MarketIntelligence:
        """Generate comprehensive morning market pulse"""
        
        # Get overnight global market movements
        global_movements = await self._get_overnight_movements()
        
        # Get pre-market indicators
        premarket_data = await self._get_premarket_indicators()
        
        # Analyze correlations
        correlations = await self.correlation_engine.analyze_global_correlations()
        
        # Get economic calendar
        economic_events = await self._get_economic_calendar()
        
        # Get sector-specific insights
        sector_insights = await self._generate_sector_insights(custom_focus)
        
        # Get institutional flow data
        institutional_flow = await self._get_institutional_flow()
        
        # Generate comprehensive summary
        summary = self._create_pulse_summary(
            global_movements,
            premarket_data,
            correlations,
            economic_events,
            sector_insights,
            institutional_flow
        )
        
        # Generate actionable recommendations
        recommendations = self._generate_recommendations(
            global_movements,
            correlations,
            sector_insights,
            institutional_flow
        )
        
        return MarketIntelligence(
            timestamp=datetime.utcnow(),
            intelligence_type=IntelligenceType.MORNING_PULSE,
            market_region=MarketRegion.INDIA,
            summary=summary,
            key_insights=self._extract_key_insights(
                global_movements, correlations, sector_insights
            ),
            data_points={
                "global_movements": global_movements,
                "premarket_data": premarket_data,
                "correlations": correlations["strongest_correlations"][:5],
                "economic_events": economic_events,
                "institutional_flow": institutional_flow
            },
            confidence_score=0.85,
            risk_level=self._assess_risk_level(global_movements, premarket_data),
            actionable_recommendations=recommendations,
            supporting_data={
                "data_sources": ["Bloomberg", "NSE", "BSE", "Reuters"],
                "analysis_time": datetime.utcnow().isoformat(),
                "market_hours_remaining": self._calculate_market_hours()
            }
        )
    
    async def _get_overnight_movements(self) -> Dict[str, Any]:
        """Get overnight movements in global markets"""
        movements = {}
        
        # US markets (previous day close)
        us_indices = ["^IXIC", "^GSPC", "^DJI"]
        for symbol in us_indices:
            try:
                data = await self.market_data.get_latest_price(symbol)
                movements[symbol] = {
                    "price": data["price"],
                    "change": data["change"],
                    "change_percent": data["change_percent"]
                }
            except:
                pass
        
        # Asian markets (current/recent close)
        asian_indices = ["^N225", "^HSI", "000001.SS"]
        for symbol in asian_indices:
            try:
                data = await self.market_data.get_latest_price(symbol)
                movements[symbol] = {
                    "price": data["price"],
                    "change": data["change"],
                    "change_percent": data["change_percent"]
                }
            except:
                pass
        
        return movements
    
    async def _get_premarket_indicators(self) -> Dict[str, Any]:
        """Get pre-market indicators for Indian markets"""
        return {
            "gift_nifty": await self._get_gift_nifty(),
            "dow_futures": await self._get_dow_futures(),
            "currency_movement": await self._get_currency_data(),
            "commodity_prices": await self._get_commodity_data(),
            "bond_yields": await self._get_bond_yields()
        }
    
    async def _get_gift_nifty(self) -> Dict[str, float]:
        """Get GIFT Nifty futures data"""
        # This would integrate with actual GIFT Nifty data
        return {
            "price": 21500.0,
            "change": 50.0,
            "change_percent": 0.23,
            "volume": 15000
        }
    
    async def _get_economic_calendar(self) -> List[Dict[str, Any]]:
        """Get today's economic events"""
        # This would integrate with economic calendar APIs
        return [
            {
                "time": "10:00",
                "event": "RBI Monetary Policy Decision",
                "importance": "high",
                "forecast": "6.50%",
                "previous": "6.50%"
            },
            {
                "time": "14:30",
                "event": "US Initial Jobless Claims",
                "importance": "medium",
                "forecast": "220K",
                "previous": "218K"
            }
        ]
    
    async def _generate_sector_insights(
        self,
        custom_focus: List[str] = None
    ) -> Dict[str, Any]:
        """Generate sector-specific insights"""
        sectors = custom_focus or ["banking", "it", "pharma", "auto", "metals"]
        insights = {}
        
        for sector in sectors:
            insights[sector] = {
                "sentiment": await self._get_sector_sentiment(sector),
                "key_stocks": await self._get_sector_leaders(sector),
                "news_impact": await self._analyze_sector_news(sector),
                "technical_outlook": await self._get_technical_outlook(sector)
            }
        
        return insights
    
    async def _get_institutional_flow(self) -> Dict[str, Any]:
        """Get institutional flow data"""
        # This would integrate with actual FII/DII data
        return {
            "fii_flow": {
                "equity": -500.0,  # Crores
                "debt": 200.0,
                "total": -300.0
            },
            "dii_flow": {
                "equity": 800.0,
                "debt": -100.0,
                "total": 700.0
            },
            "net_flow": 400.0,
            "trend": "positive"
        }
    
    def _create_pulse_summary(self, *args) -> str:
        """Create comprehensive pulse summary"""
        global_movements, premarket_data, correlations, events, sectors, flows = args
        
        # Analyze overall market sentiment
        positive_signals = 0
        negative_signals = 0
        
        # Count global market signals
        for symbol, data in global_movements.items():
            if data.get("change_percent", 0) > 0:
                positive_signals += 1
            else:
                negative_signals += 1
        
        # Overall sentiment
        if positive_signals > negative_signals:
            sentiment = "positive"
            sentiment_desc = "Global markets show positive momentum"
        elif negative_signals > positive_signals:
            sentiment = "negative"
            sentiment_desc = "Global markets face headwinds"
        else:
            sentiment = "neutral"
            sentiment_desc = "Mixed signals from global markets"
        
        summary = f"""
        **Morning Market Pulse - {datetime.now().strftime('%B %d, %Y')}**
        
        **Overall Sentiment: {sentiment.upper()}**
        {sentiment_desc}. 
        
        **Key Highlights:**
        • GIFT Nifty: {premarket_data.get('gift_nifty', {}).get('change_percent', 0):.2f}% 
        • Net Institutional Flow: ₹{flows['net_flow']:.0f}Cr ({flows['trend']})
        • Strongest Global Correlation: {correlations['strongest_correlations'][0]['global_market']} - {correlations['strongest_correlations'][0]['indian_market']}
        
        **Today's Focus:**
        • {len(events)} major economic events scheduled
        • Watch for sector rotation in {', '.join(list(sectors.keys())[:3])}
        • Currency at {premarket_data.get('currency_movement', {}).get('usd_inr', 83.0):.2f}
        """
        
        return summary.strip()
    
    def _extract_key_insights(self, *args) -> List[str]:
        """Extract key actionable insights"""
        global_movements, correlations, sectors = args
        
        insights = []
        
        # Global market insight
        if global_movements:
            strongest_move = max(
                global_movements.items(),
                key=lambda x: abs(x[1].get("change_percent", 0))
            )
            insights.append(
                f"{strongest_move[0]} moved {strongest_move[1].get('change_percent', 0):.2f}%, "
                f"likely to impact correlated Indian indices"
            )
        
        # Correlation insight
        if correlations.get("strongest_correlations"):
            top_corr = correlations["strongest_correlations"][0]
            insights.append(
                f"Monitor {top_corr['global_market']} for {top_corr['indian_market']} direction "
                f"(correlation: {top_corr['correlation']:.3f})"
            )
        
        # Sector insight
        if sectors:
            sector_names = list(sectors.keys())
            insights.append(
                f"Focus sectors: {', '.join(sector_names[:3])} showing "
                f"potential for outperformance"
            )
        
        return insights
    
    def _generate_recommendations(self, *args) -> List[str]:
        """Generate actionable trading recommendations"""
        global_movements, correlations, sectors, flows = args
        
        recommendations = []
        
        # Flow-based recommendation
        if flows['net_flow'] > 300:
            recommendations.append(
                "Strong institutional inflows suggest buying interest. "
                "Consider long positions in large-cap stocks."
            )
        elif flows['net_flow'] < -300:
            recommendations.append(
                "Institutional outflows indicate caution. "
                "Consider defensive positioning or hedging strategies."
            )
        
        # Correlation-based recommendation
        if correlations.get("strongest_correlations"):
            top_corr = correlations["strongest_correlations"][0]
            if abs(top_corr["correlation"]) > 0.7:
                recommendations.append(
                    f"Use {top_corr['global_market']} as leading indicator for "
                    f"{top_corr['indian_market']} trades."
                )
        
        # Sector rotation recommendation
        if sectors:
            recommendations.append(
                "Sector rotation opportunities identified. "
                "Review detailed sector analysis for positioning."
            )
        
        return recommendations
    
    def _assess_risk_level(self, global_movements: Dict, premarket_data: Dict) -> str:
        """Assess overall market risk level"""
        risk_factors = 0
        
        # High volatility in global markets
        for symbol, data in global_movements.items():
            if abs(data.get("change_percent", 0)) > 2:
                risk_factors += 1
        
        # Currency volatility
        if abs(premarket_data.get("currency_movement", {}).get("change_percent", 0)) > 0.5:
            risk_factors += 1
        
        # VIX levels (simplified)
        if premarket_data.get("vix", 20) > 25:
            risk_factors += 2
        
        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 1:
            return "medium"
        else:
            return "low"
    
    def _calculate_market_hours(self) -> str:
        """Calculate remaining market hours"""
        now = datetime.now()
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now < market_close:
            remaining = market_close - now
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            return "Market closed"


class IntelligenceEngine:
    """
    Main Intelligence Engine orchestrating all intelligence services
    """
    
    def __init__(self):
        self.correlation_engine = GlobalCorrelationEngine()
        self.morning_pulse = MorningPulseGenerator()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def process_intelligence_request(
        self,
        request: IntelligenceRequest,
        db: AsyncSession
    ) -> MarketIntelligence:
        """Process intelligence request and generate appropriate intelligence"""
        
        if request.intelligence_type == IntelligenceType.MORNING_PULSE:
            intelligence = await self.morning_pulse.generate_morning_pulse(
                request.client_id,
                request.custom_parameters.get("focus_sectors")
            )
        
        elif request.intelligence_type == IntelligenceType.CORRELATION_ANALYSIS:
            correlation_data = await self.correlation_engine.analyze_global_correlations(
                request.custom_parameters.get("timeframe", "30d")
            )
            intelligence = self._format_correlation_intelligence(correlation_data)
        
        else:
            # Handle other intelligence types
            intelligence = await self._generate_custom_intelligence(request)
        
        # Log usage
        await self._log_intelligence_usage(request, intelligence, db)
        
        # Deliver intelligence
        await self._deliver_intelligence(request, intelligence)
        
        return intelligence
    
    async def _deliver_intelligence(
        self,
        request: IntelligenceRequest,
        intelligence: MarketIntelligence
    ):
        """Deliver intelligence in requested format"""
        
        if request.delivery_format == DeliveryFormat.EMAIL_DIGEST:
            await self._send_email_digest(request, intelligence)
        
        elif request.delivery_format == DeliveryFormat.WHATSAPP_SUMMARY:
            await self._send_whatsapp_summary(request, intelligence)
        
        elif request.delivery_format == DeliveryFormat.API_WEBHOOK:
            await self._send_webhook(request, intelligence)
        
        # Always store in cache for API access
        cache_key = f"intelligence:{request.client_id}:{request.intelligence_type.value}"
        self.redis_client.setex(
            cache_key,
            86400,  # 24 hours
            json.dumps(intelligence.__dict__, default=str)
        )
    
    async def _log_intelligence_usage(
        self,
        request: IntelligenceRequest,
        intelligence: MarketIntelligence,
        db: AsyncSession
    ):
        """Log usage for billing"""
        
        usage_record = UsageRecord(
            client_id=request.client_id,
            service_type="ai_suite",
            service_name="intelligence_engine",
            endpoint=f"intelligence_{request.intelligence_type.value}",
            timestamp=datetime.utcnow(),
            request_count=1,
            billable_units=1.0,
            unit_cost=5.0,  # $5 per intelligence report
            total_cost=5.0,
            metrics={
                "intelligence_type": request.intelligence_type.value,
                "market_regions": [r.value for r in request.market_regions],
                "delivery_format": request.delivery_format.value,
                "confidence_score": intelligence.confidence_score
            }
        )
        
        db.add(usage_record)
        await db.commit()


# Dependency injection
intelligence_engine = IntelligenceEngine()

async def get_intelligence_engine() -> IntelligenceEngine:
    """Get intelligence engine instance"""
    return intelligence_engine