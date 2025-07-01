"""
AI Intelligence Service - Global Morning Pulse Engine
Intelligence-as-a-Service providing pre-market insights and correlation analysis
"""

import asyncio
import openai
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum
import logging
import json
import aiohttp
import asyncpg
from decimal import Decimal

logger = logging.getLogger(__name__)


class UserTier(Enum):
    LITE = "lite"
    PRO = "pro"
    BLACK = "black"


class MarketRegion(Enum):
    US = "us"
    EUROPE = "europe"
    ASIA = "asia"
    COMMODITY = "commodity"
    FOREX = "forex"


@dataclass
class GlobalMarketData:
    """Global market data structure"""
    symbol: str
    region: MarketRegion
    current_price: float
    change_percent: float
    change_absolute: float
    volume: int
    timestamp: datetime
    market_cap: Optional[float] = None
    news_sentiment: Optional[float] = None


@dataclass
class TradingIdea:
    """AI-generated trading idea"""
    symbol: str
    action: str  # BUY/SELL/HOLD
    entry_price: float
    stop_loss: float
    target_price: float
    confidence: float
    rationale: str
    timeframe: str
    risk_level: str
    expected_return: float
    correlation_source: str


@dataclass
class MorningPulseReport:
    """Complete morning pulse report"""
    timestamp: datetime
    global_triggers: List[Dict[str, Any]]
    india_correlations: List[Dict[str, Any]]
    trade_ideas: List[TradingIdea]
    risk_alerts: List[str]
    institutional_flows: Dict[str, Any]
    voice_note_url: Optional[str]
    text_summary: str
    user_tier: UserTier


class GlobalDataFeedManager:
    """Manages global market data feeds"""
    
    def __init__(self):
        self.data_sources = {
            "yahoo_finance": yf,
            "alpha_vantage": None,  # Will be initialized with API key
            "news_api": None
        }
        
        # Key global symbols to track
        self.tracked_symbols = {
            MarketRegion.US: ["^IXIC", "^GSPC", "^DJI", "QQQ", "SPY"],
            MarketRegion.EUROPE: ["^FTSE", "^GDAXI", "^FCHI"],
            MarketRegion.ASIA: ["^N225", "^HSI", "000001.SS"],
            MarketRegion.COMMODITY: ["CL=F", "GC=F", "SI=F", "BZ=F"],
            MarketRegion.FOREX: ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "INRUSD=X"]
        }
        
        # India correlation mappings
        self.correlation_mappings = {
            "^IXIC": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "LTI.NS"],
            "CL=F": ["ONGC.NS", "IOC.NS", "BPCL.NS", "HPCL.NS", "RELIANCE.NS"],
            "GC=F": ["TANISHQ.NS", "TITAN.NS", "KALYAN.NS"],
            "^GSPC": ["NIFTY", "SENSEX", "BANKNIFTY"],
            "EURUSD=X": ["BHARTIARTL.NS", "TCS.NS", "INFY.NS"]
        }
    
    async def get_overnight_global_data(self) -> List[GlobalMarketData]:
        """Fetch overnight global market data"""
        
        global_data = []
        
        for region, symbols in self.tracked_symbols.items():
            for symbol in symbols:
                try:
                    data = await self._fetch_symbol_data(symbol, region)
                    if data:
                        global_data.append(data)
                except Exception as e:
                    logger.error(f"Failed to fetch data for {symbol}: {e}")
        
        return global_data
    
    async def _fetch_symbol_data(self, symbol: str, region: MarketRegion) -> Optional[GlobalMarketData]:
        """Fetch data for a specific symbol"""
        
        try:
            # Use yfinance for real-time data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d", interval="1d")
            
            if len(hist) < 2:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2])
            change_absolute = current_price - prev_price
            change_percent = (change_absolute / prev_price) * 100
            volume = int(hist['Volume'].iloc[-1])
            
            return GlobalMarketData(
                symbol=symbol,
                region=region,
                current_price=current_price,
                change_percent=change_percent,
                change_absolute=change_absolute,
                volume=volume,
                timestamp=datetime.now(timezone.utc),
                news_sentiment=await self._get_news_sentiment(symbol)
            )
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def _get_news_sentiment(self, symbol: str) -> float:
        """Get news sentiment for a symbol (simplified)"""
        
        # In production, this would use NewsAPI or similar
        # For now, return neutral sentiment
        return 0.0


class CorrelationEngine:
    """Analyzes global-to-India market correlations"""
    
    def __init__(self):
        self.correlation_models = {}
        self.historical_correlations = {}
        
        # Predefined correlation strengths (would be ML-learned in production)
        self.base_correlations = {
            ("^IXIC", "TCS.NS"): 0.75,
            ("^IXIC", "INFY.NS"): 0.73,
            ("CL=F", "ONGC.NS"): 0.68,
            ("CL=F", "IOC.NS"): -0.45,  # Negative for refineries
            ("GC=F", "TITAN.NS"): 0.42,
            ("EURUSD=X", "BHARTIARTL.NS"): 0.35
        }
    
    async def analyze_india_impact(self, global_data: List[GlobalMarketData]) -> List[Dict[str, Any]]:
        """Analyze impact of global moves on Indian stocks"""
        
        correlations = []
        
        for global_point in global_data:
            if abs(global_point.change_percent) > 1.0:  # Significant moves only
                impact = await self._calculate_impact(global_point)
                if impact:
                    correlations.append(impact)
        
        return correlations
    
    async def _calculate_impact(self, global_data: GlobalMarketData) -> Optional[Dict[str, Any]]:
        """Calculate impact of global move on Indian stocks"""
        
        impacted_stocks = []
        
        # Find correlated Indian stocks
        if global_data.symbol in self.correlation_mappings:
            indian_symbols = self.correlation_mappings[global_data.symbol]
            
            for indian_symbol in indian_symbols:
                correlation_key = (global_data.symbol, indian_symbol)
                
                if correlation_key in self.base_correlations:
                    correlation_strength = self.base_correlations[correlation_key]
                    
                    expected_impact = global_data.change_percent * correlation_strength
                    
                    impacted_stocks.append({
                        "symbol": indian_symbol.replace(".NS", ""),
                        "expected_impact": round(expected_impact, 2),
                        "correlation_strength": correlation_strength,
                        "confidence": abs(correlation_strength)
                    })
        
        if impacted_stocks:
            return {
                "global_trigger": {
                    "symbol": global_data.symbol,
                    "change": global_data.change_percent,
                    "region": global_data.region.value
                },
                "india_impact": impacted_stocks,
                "impact_magnitude": max([abs(stock["expected_impact"]) for stock in impacted_stocks])
            }
        
        return None


class TradingIdeaGenerator:
    """Generates AI-powered trading ideas"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
        self.risk_profiles = {
            UserTier.LITE: {"max_risk": 2, "conservative": True},
            UserTier.PRO: {"max_risk": 5, "conservative": False},
            UserTier.BLACK: {"max_risk": 10, "conservative": False}
        }
    
    async def generate_ideas(
        self, 
        correlations: List[Dict[str, Any]], 
        user_tier: UserTier
    ) -> List[TradingIdea]:
        """Generate trading ideas based on correlations"""
        
        ideas = []
        risk_profile = self.risk_profiles[user_tier]
        
        for correlation in correlations[:3]:  # Top 3 correlations
            if correlation["impact_magnitude"] > 1.0:  # Significant impact
                idea = await self._generate_idea_for_correlation(correlation, risk_profile)
                if idea:
                    ideas.append(idea)
        
        return ideas
    
    async def _generate_idea_for_correlation(
        self, 
        correlation: Dict[str, Any], 
        risk_profile: Dict[str, Any]
    ) -> Optional[TradingIdea]:
        """Generate a specific trading idea"""
        
        global_trigger = correlation["global_trigger"]
        best_impact = max(correlation["india_impact"], key=lambda x: abs(x["expected_impact"]))
        
        symbol = best_impact["symbol"]
        expected_impact = best_impact["expected_impact"]
        
        # Determine action
        action = "BUY" if expected_impact > 0 else "SELL"
        
        # Get current price (simplified - would use real-time data)
        current_price = await self._get_current_price(symbol)
        if not current_price:
            return None
        
        # Calculate entry, stop loss, and target
        entry_price = current_price
        
        if action == "BUY":
            target_price = current_price * (1 + abs(expected_impact) / 100)
            stop_loss = current_price * (1 - risk_profile["max_risk"] / 100)
        else:
            target_price = current_price * (1 - abs(expected_impact) / 100)
            stop_loss = current_price * (1 + risk_profile["max_risk"] / 100)
        
        # Calculate expected return
        expected_return = abs((target_price - entry_price) / entry_price * 100)
        
        # Generate rationale
        rationale = f"{global_trigger['symbol']} {'+' if global_trigger['change'] > 0 else ''}{global_trigger['change']:.1f}% → {symbol} correlation play"
        
        return TradingIdea(
            symbol=symbol,
            action=action,
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            target_price=round(target_price, 2),
            confidence=best_impact["confidence"],
            rationale=rationale,
            timeframe="intraday" if abs(expected_impact) < 3 else "swing",
            risk_level="low" if risk_profile["conservative"] else "medium",
            expected_return=round(expected_return, 2),
            correlation_source=global_trigger["symbol"]
        )
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for Indian stock (simplified)"""
        
        try:
            # Add .NS suffix for NSE
            yf_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
        except:
            pass
        
        # Fallback dummy prices for demo
        dummy_prices = {
            "TCS": 3900, "INFY": 1450, "ONGC": 220, "IOC": 85,
            "RELIANCE": 2500, "TITAN": 3200, "HCLTECH": 1180
        }
        
        return dummy_prices.get(symbol, 1000)


class VoiceGenerator:
    """Generates voice notes for morning pulse"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI()
    
    async def generate_voice_summary(
        self, 
        pulse_report: MorningPulseReport,
        language: str = "english"
    ) -> str:
        """Generate voice note summary"""
        
        # Create voice script
        script = await self._create_voice_script(pulse_report, language)
        
        # In production, this would use text-to-speech API
        # For now, return the script text
        return script
    
    async def _create_voice_script(self, report: MorningPulseReport, language: str) -> str:
        """Create script for voice note"""
        
        prompt = f"""
Create a 30-second voice script for Indian traders in {language}.

Global Triggers:
{json.dumps([trigger for trigger in report.global_triggers], indent=2)}

Trading Ideas:
{json.dumps([{
    'symbol': idea.symbol,
    'action': idea.action,
    'price': idea.entry_price,
    'rationale': idea.rationale
} for idea in report.trade_ideas], indent=2)}

Requirements:
- 30 seconds when spoken
- Clear, confident tone
- Focus on actionable insights
- Include risk warnings
- Use Indian context

Return only the script text.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Voice script generation failed: {e}")
            return self._fallback_script(report)
    
    def _fallback_script(self, report: MorningPulseReport) -> str:
        """Fallback script when AI fails"""
        
        script = "Good morning! Here's your market pulse. "
        
        if report.global_triggers:
            trigger = report.global_triggers[0]
            script += f"Overnight, {trigger.get('market', 'global markets')} moved {trigger.get('change', 'significantly')}. "
        
        if report.trade_ideas:
            idea = report.trade_ideas[0]
            script += f"Consider {idea.action.lower()}ing {idea.symbol} around {idea.entry_price}. "
        
        script += "Trade responsibly. Have a profitable day!"
        
        return script


class AIIntelligenceService:
    """Main AI Intelligence Service"""
    
    def __init__(self):
        self.data_manager = GlobalDataFeedManager()
        self.correlation_engine = CorrelationEngine()
        self.idea_generator = TradingIdeaGenerator()
        self.voice_generator = VoiceGenerator()
        
        # Cache for performance
        self.cache = {}
        self.cache_expiry = timedelta(minutes=15)
    
    async def generate_morning_pulse(
        self, 
        user_id: str, 
        user_tier: UserTier = UserTier.PRO
    ) -> MorningPulseReport:
        """Generate complete morning pulse report"""
        
        try:
            # Check cache first
            cache_key = f"morning_pulse_{user_tier.value}"
            if self._is_cache_valid(cache_key):
                cached_report = self.cache[cache_key]["data"]
                # Personalize cached report
                return await self._personalize_report(cached_report, user_id)
            
            # Step 1: Get global market data
            global_data = await self.data_manager.get_overnight_global_data()
            
            # Step 2: Analyze India correlations
            correlations = await self.correlation_engine.analyze_india_impact(global_data)
            
            # Step 3: Generate trading ideas
            trade_ideas = await self.idea_generator.generate_ideas(correlations, user_tier)
            
            # Step 4: Extract global triggers
            global_triggers = self._extract_global_triggers(global_data)
            
            # Step 5: Generate risk alerts
            risk_alerts = await self._generate_risk_alerts(global_data)
            
            # Step 6: Get institutional flows (mock for now)
            institutional_flows = await self._get_institutional_flows(user_tier)
            
            # Step 7: Create report
            report = MorningPulseReport(
                timestamp=datetime.now(timezone.utc),
                global_triggers=global_triggers,
                india_correlations=correlations,
                trade_ideas=trade_ideas,
                risk_alerts=risk_alerts,
                institutional_flows=institutional_flows,
                voice_note_url=None,  # Will be generated separately
                text_summary="",
                user_tier=user_tier
            )
            
            # Step 8: Generate voice note
            if user_tier in [UserTier.PRO, UserTier.BLACK]:
                voice_script = await self.voice_generator.generate_voice_summary(report)
                report.voice_note_url = f"https://gridworks.ai/voice/{user_id}_{datetime.now().strftime('%Y%m%d')}.mp3"
                report.text_summary = voice_script
            
            # Cache the report
            self.cache[cache_key] = {
                "data": report,
                "timestamp": datetime.now()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Morning pulse generation failed: {e}")
            return await self._create_fallback_report(user_tier)
    
    def _extract_global_triggers(self, global_data: List[GlobalMarketData]) -> List[Dict[str, Any]]:
        """Extract significant global market triggers"""
        
        triggers = []
        
        for data in global_data:
            if abs(data.change_percent) > 1.0:  # Significant moves
                trigger = {
                    "market": self._get_market_name(data.symbol),
                    "symbol": data.symbol,
                    "change": round(data.change_percent, 2),
                    "price": data.current_price,
                    "region": data.region.value,
                    "impact_level": "high" if abs(data.change_percent) > 2.0 else "medium"
                }
                triggers.append(trigger)
        
        # Sort by impact magnitude
        triggers.sort(key=lambda x: abs(x["change"]), reverse=True)
        
        return triggers[:5]  # Top 5 triggers
    
    def _get_market_name(self, symbol: str) -> str:
        """Convert symbol to readable market name"""
        
        name_map = {
            "^IXIC": "NASDAQ",
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "CL=F": "Crude Oil",
            "GC=F": "Gold",
            "^NSEI": "Nifty 50"
        }
        
        return name_map.get(symbol, symbol)
    
    async def _generate_risk_alerts(self, global_data: List[GlobalMarketData]) -> List[str]:
        """Generate risk alerts based on market conditions"""
        
        alerts = []
        
        # Check for high volatility
        high_vol_count = sum(1 for data in global_data if abs(data.change_percent) > 2.0)
        if high_vol_count > 2:
            alerts.append("High global volatility detected - trade with caution")
        
        # Check for specific risk events (simplified)
        for data in global_data:
            if data.symbol == "CL=F" and abs(data.change_percent) > 3.0:
                alerts.append("Oil volatility may impact energy stocks")
            elif data.symbol == "^IXIC" and data.change_percent < -2.0:
                alerts.append("Tech sell-off may pressure Indian IT stocks")
        
        # Add time-based alerts
        current_hour = datetime.now().hour
        if current_hour == 18:  # 6 PM IST
            alerts.append("US Fed speech scheduled - expect volatility spike")
        
        return alerts
    
    async def _get_institutional_flows(self, user_tier: UserTier) -> Dict[str, Any]:
        """Get institutional flow data (mock implementation)"""
        
        if user_tier == UserTier.BLACK:
            return {
                "fii_activity": {
                    "net_investment": -200,  # Million USD
                    "focus_sectors": ["IT", "Pharma"],
                    "activity_level": "high"
                },
                "dii_activity": {
                    "net_investment": 1500,  # Million INR
                    "focus_sectors": ["Banking", "Auto"],
                    "activity_level": "moderate"
                },
                "block_deals": [
                    {"stock": "RELIANCE", "value": 500, "buyer": "LIC"}
                ]
            }
        elif user_tier == UserTier.PRO:
            return {
                "fii_activity": {"net_investment": -200, "activity_level": "high"},
                "dii_activity": {"net_investment": 1500, "activity_level": "moderate"}
            }
        else:
            return {}
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_expiry
    
    async def _personalize_report(self, base_report: MorningPulseReport, user_id: str) -> MorningPulseReport:
        """Personalize cached report for specific user"""
        
        # In production, this would customize based on user preferences
        # For now, return the base report
        return base_report
    
    async def _create_fallback_report(self, user_tier: UserTier) -> MorningPulseReport:
        """Create fallback report when main generation fails"""
        
        return MorningPulseReport(
            timestamp=datetime.now(timezone.utc),
            global_triggers=[{
                "market": "Market Data",
                "change": 0,
                "impact_level": "low"
            }],
            india_correlations=[],
            trade_ideas=[],
            risk_alerts=["Market data temporarily unavailable"],
            institutional_flows={},
            voice_note_url=None,
            text_summary="Good morning! Market data is being updated. Please check back in a few minutes.",
            user_tier=user_tier
        )
    
    async def get_custom_alert(self, user_id: str, trigger_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom alerts based on user configuration"""
        
        # Example: "Alert me if Bitcoin affects IT stocks"
        if trigger_config.get("condition") == "bitcoin_it_correlation":
            btc_data = await self._fetch_bitcoin_data()
            if btc_data and abs(btc_data.change_percent) > 5.0:
                return {
                    "triggered": True,
                    "message": f"Bitcoin moved {btc_data.change_percent:.1f}% - IT stocks may be impacted",
                    "recommended_action": "Monitor TCS, Infosys for correlation moves"
                }
        
        return {"triggered": False}
    
    async def _fetch_bitcoin_data(self) -> Optional[GlobalMarketData]:
        """Fetch Bitcoin data"""
        
        try:
            ticker = yf.Ticker("BTC-USD")
            hist = ticker.history(period="2d", interval="1d")
            
            if len(hist) >= 2:
                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2])
                change_percent = ((current_price - prev_price) / prev_price) * 100
                
                return GlobalMarketData(
                    symbol="BTC-USD",
                    region=MarketRegion.COMMODITY,
                    current_price=current_price,
                    change_percent=change_percent,
                    change_absolute=current_price - prev_price,
                    volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                    timestamp=datetime.now(timezone.utc)
                )
        except Exception as e:
            logger.error(f"Bitcoin data fetch failed: {e}")
            
        return None