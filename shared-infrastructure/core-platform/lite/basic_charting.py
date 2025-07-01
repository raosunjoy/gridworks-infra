"""
GridWorks LITE Basic Charting
============================

Simple, fast charting features for mass market users.
Optimized for WhatsApp integration and minimal complexity.

LITE Features (Free):
- Basic candlestick charts
- 5 essential indicators (SMA, EMA, RSI, MACD, Bollinger)
- Simple drawing tools (trendlines, rectangles)
- 3 timeframes (15m, 1h, 1d)
- Basic price alerts
- WhatsApp chart sharing

Focus: Speed, simplicity, and accessibility for first-time investors.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class LiteTimeFrame(Enum):
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    DAILY = "1d"


class LiteIndicator(Enum):
    SMA = "SMA"  # Simple Moving Average
    EMA = "EMA"  # Exponential Moving Average  
    RSI = "RSI"  # Relative Strength Index
    MACD = "MACD"  # MACD
    BOLLINGER = "BB"  # Bollinger Bands


@dataclass
class BasicChart:
    chart_id: str
    user_id: str
    symbol: str
    timeframe: LiteTimeFrame
    created_at: datetime
    last_updated: datetime


@dataclass
class BasicCandle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass
class SimpleIndicator:
    name: str
    values: List[float]
    color: str = "blue"


@dataclass
class PriceAlert:
    alert_id: str
    user_id: str
    symbol: str
    price: float
    condition: str  # "above" or "below"
    is_active: bool = True
    created_at: datetime = None


class BasicChartingEngine:
    """Simplified charting engine for GridWorks LITE users."""
    
    def __init__(self):
        self.lite_charts = {}  # chart_id -> BasicChart
        self.chart_data = {}   # chart_id -> List[BasicCandle]
        self.lite_alerts = {}  # user_id -> List[PriceAlert]
        
        # Simplified market data (in production, would connect to data feed)
        self.market_prices = {
            "RELIANCE": 2500.0,
            "TCS": 3200.0,
            "HDFC": 1600.0,
            "INFY": 1400.0,
            "ITC": 450.0
        }
    
    async def create_lite_chart(self, user_id: str, symbol: str, 
                               timeframe: LiteTimeFrame = LiteTimeFrame.ONE_HOUR) -> str:
        """Create a basic chart for LITE user."""
        chart_id = f"lite_{user_id}_{symbol}_{int(time.time())}"
        
        chart = BasicChart(
            chart_id=chart_id,
            user_id=user_id,
            symbol=symbol,
            timeframe=timeframe,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.lite_charts[chart_id] = chart
        
        # Load basic historical data
        self.chart_data[chart_id] = await self._load_basic_data(symbol, timeframe)
        
        logger.info(f"Created LITE chart {chart_id} for {symbol}")
        return chart_id
    
    async def get_basic_indicators(self, chart_id: str, 
                                  indicator: LiteIndicator) -> SimpleIndicator:
        """Calculate basic indicators for LITE users."""
        if chart_id not in self.chart_data:
            raise ValueError("Chart not found")
        
        candles = self.chart_data[chart_id]
        closes = [candle.close for candle in candles]
        
        if indicator == LiteIndicator.SMA:
            values = self._calculate_simple_sma(closes, 20)
            return SimpleIndicator("SMA(20)", values, "blue")
            
        elif indicator == LiteIndicator.EMA:
            values = self._calculate_simple_ema(closes, 20)
            return SimpleIndicator("EMA(20)", values, "orange")
            
        elif indicator == LiteIndicator.RSI:
            values = self._calculate_simple_rsi(closes, 14)
            return SimpleIndicator("RSI(14)", values, "purple")
            
        elif indicator == LiteIndicator.MACD:
            macd_values = self._calculate_simple_macd(closes)
            return SimpleIndicator("MACD", macd_values, "red")
            
        elif indicator == LiteIndicator.BOLLINGER:
            bb_values = self._calculate_simple_bollinger(closes, 20)
            return SimpleIndicator("BB(20)", bb_values, "gray")
        
        return SimpleIndicator("Unknown", [], "black")
    
    async def set_price_alert(self, user_id: str, symbol: str, 
                             price: float, condition: str) -> str:
        """Set a simple price alert for LITE user."""
        alert_id = f"alert_{user_id}_{symbol}_{int(time.time())}"
        
        alert = PriceAlert(
            alert_id=alert_id,
            user_id=user_id,
            symbol=symbol,
            price=price,
            condition=condition,
            created_at=datetime.now()
        )
        
        if user_id not in self.lite_alerts:
            self.lite_alerts[user_id] = []
        
        self.lite_alerts[user_id].append(alert)
        
        logger.info(f"Created LITE alert: {symbol} {condition} {price}")
        return alert_id
    
    async def generate_whatsapp_chart_summary(self, chart_id: str) -> str:
        """Generate a simple chart summary for WhatsApp sharing."""
        if chart_id not in self.lite_charts:
            return "Chart not found"
        
        chart = self.lite_charts[chart_id]
        candles = self.chart_data[chart_id]
        
        if not candles:
            return f"{chart.symbol} - No data available"
        
        latest = candles[-1]
        previous = candles[-2] if len(candles) > 1 else latest
        
        change = latest.close - previous.close
        change_pct = (change / previous.close) * 100
        
        # Simple trend analysis
        trend = "📈 Rising" if change > 0 else "📉 Falling" if change < 0 else "➡️ Flat"
        
        # Basic support/resistance (simplified)
        highs = [c.high for c in candles[-10:]]
        lows = [c.low for c in candles[-10:]]
        support = min(lows)
        resistance = max(highs)
        
        summary = f"""📊 *{chart.symbol} Chart Summary*
        
💰 Current Price: ₹{latest.close:.2f}
📊 Change: {change:+.2f} ({change_pct:+.1f}%)
📈 Trend: {trend}

📍 Support: ₹{support:.2f}
📍 Resistance: ₹{resistance:.2f}
📊 Volume: {latest.volume:,}

⏰ Updated: {latest.timestamp.strftime('%H:%M')}
🎯 Timeframe: {chart.timeframe.value}

_GridWorks LITE - Simple Trading Made Easy_"""
        
        return summary
    
    async def _load_basic_data(self, symbol: str, timeframe: LiteTimeFrame, 
                              days: int = 7) -> List[BasicCandle]:
        """Load simplified historical data for LITE users."""
        candles = []
        start_price = self.market_prices.get(symbol, 1000.0)
        
        # Generate simplified data
        for i in range(days * 24):  # Hourly data for demo
            timestamp = datetime.now() - timedelta(hours=days * 24 - i)
            
            # Simple random walk
            if i == 0:
                price = start_price
            else:
                price = candles[-1].close + ((-1 if i % 3 == 0 else 1) * (i % 10))
            
            candle = BasicCandle(
                timestamp=timestamp,
                open=price + (i % 3),
                high=price + (i % 5) + 5,
                low=price - (i % 4) - 3,
                close=price + (i % 2),
                volume=1000 + (i * 100)
            )
            candles.append(candle)
        
        return candles
    
    def _calculate_simple_sma(self, data: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average (simplified)."""
        if len(data) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(data)):
            avg = sum(data[i - period + 1:i + 1]) / period
            sma_values.append(avg)
        
        return sma_values[-20:]  # Return last 20 values for LITE
    
    def _calculate_simple_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average (simplified)."""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        ema_values = [ema]
        
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values[-20:]  # Return last 20 values for LITE
    
    def _calculate_simple_rsi(self, data: List[float], period: int = 14) -> List[float]:
        """Calculate RSI (simplified for LITE)."""
        if len(data) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values[-20:]  # Return last 20 values for LITE
    
    def _calculate_simple_macd(self, data: List[float]) -> List[float]:
        """Calculate MACD (simplified for LITE)."""
        if len(data) < 26:
            return []
        
        ema12 = self._calculate_simple_ema(data, 12)
        ema26 = self._calculate_simple_ema(data, 26)
        
        # Align arrays
        min_length = min(len(ema12), len(ema26))
        macd_line = []
        
        for i in range(min_length):
            macd = ema12[-(min_length-i)] - ema26[-(min_length-i)]
            macd_line.append(macd)
        
        return macd_line[-20:]  # Return last 20 values for LITE
    
    def _calculate_simple_bollinger(self, data: List[float], period: int = 20) -> List[float]:
        """Calculate Bollinger Bands middle line (simplified for LITE)."""
        return self._calculate_simple_sma(data, period)
    
    def check_lite_alerts(self, symbol: str, current_price: float):
        """Check if any LITE alerts should be triggered."""
        for user_id, alerts in self.lite_alerts.items():
            for alert in alerts:
                if alert.symbol == symbol and alert.is_active:
                    triggered = False
                    
                    if alert.condition == "above" and current_price >= alert.price:
                        triggered = True
                    elif alert.condition == "below" and current_price <= alert.price:
                        triggered = True
                    
                    if triggered:
                        alert.is_active = False
                        self._send_lite_alert(alert, current_price)
    
    def _send_lite_alert(self, alert: PriceAlert, current_price: float):
        """Send simple alert notification for LITE users."""
        message = f"""🚨 *Price Alert Triggered!*
        
💰 {alert.symbol}: ₹{current_price:.2f}
🎯 Alert: {alert.condition.title()} ₹{alert.price:.2f}

_GridWorks LITE Alert_"""
        
        logger.info(f"LITE Alert: {alert.symbol} {alert.condition} {alert.price}")
        
        # In production, send to WhatsApp
        # self.whatsapp_client.send_message(alert.user_id, message)


class LiteChartMessaging:
    """Handle chart-related WhatsApp messages for LITE users."""
    
    def __init__(self, charting_engine: BasicChartingEngine):
        self.charting_engine = charting_engine
    
    async def process_chart_request(self, user_id: str, message: str) -> str:
        """Process chart-related messages from LITE users."""
        message_lower = message.lower()
        
        if "chart" in message_lower or "graph" in message_lower:
            return await self._handle_chart_request(user_id, message)
        elif "alert" in message_lower:
            return await self._handle_alert_request(user_id, message)
        elif "indicator" in message_lower or "sma" in message_lower or "rsi" in message_lower:
            return await self._handle_indicator_request(user_id, message)
        else:
            return self._get_chart_help()
    
    async def _handle_chart_request(self, user_id: str, message: str) -> str:
        """Handle chart creation requests."""
        # Extract symbol from message
        symbol = self._extract_symbol(message)
        if not symbol:
            return """📊 *Chart Request*

Please specify a stock symbol:
• "Show Reliance chart"
• "TCS chart please"  
• "HDFC graph"

🎯 Available: RELIANCE, TCS, HDFC, INFY, ITC"""
        
        try:
            chart_id = await self.charting_engine.create_lite_chart(user_id, symbol)
            summary = await self.charting_engine.generate_whatsapp_chart_summary(chart_id)
            
            return f"{summary}\n\n💡 *Try these commands:*\n• \"Add RSI indicator\"\n• \"Set alert at 2600\"\n• \"Show support resistance\""
            
        except Exception as e:
            return f"❌ Sorry, couldn't create chart for {symbol}. Please try again."
    
    async def _handle_alert_request(self, user_id: str, message: str) -> str:
        """Handle price alert requests."""
        # Simple parsing for LITE users
        import re
        
        # Extract price and symbol
        price_match = re.search(r'(\d+\.?\d*)', message)
        symbol = self._extract_symbol(message)
        condition = "above" if "above" in message.lower() or "upar" in message.lower() else "below"
        
        if not price_match or not symbol:
            return """🚨 *Set Price Alert*

Please specify symbol and price:
• "Alert Reliance above 2600"
• "Notify TCS below 3000"
• "Alert HDFC at 1650"

💡 We'll send you a WhatsApp message when the price is reached!"""
        
        price = float(price_match.group(1))
        
        try:
            alert_id = await self.charting_engine.set_price_alert(user_id, symbol, price, condition)
            
            return f"""✅ *Alert Set Successfully!*

📊 Stock: {symbol}
💰 Price: ₹{price}
🎯 Condition: {condition.title()}

🔔 You'll get a WhatsApp message when {symbol} goes {condition} ₹{price}

_GridWorks LITE - Simple Alerts_"""
            
        except Exception as e:
            return "❌ Couldn't set alert. Please try again."
    
    async def _handle_indicator_request(self, user_id: str, message: str) -> str:
        """Handle technical indicator requests for LITE users."""
        # For LITE, provide simple explanations rather than complex charts
        message_lower = message.lower()
        
        if "sma" in message_lower or "moving average" in message_lower:
            return """📈 *Simple Moving Average (SMA)*

🎯 *What it shows:* Average price over last 20 days
📊 *How to use:* 
• Price above SMA = Uptrend 📈
• Price below SMA = Downtrend 📉

💡 *Upgrade to GridWorks PRO* for live SMA charts and advanced indicators!

_LITE users get explanations, PRO users get live charts_ 🚀"""
        
        elif "rsi" in message_lower:
            return """⚡ *RSI (Relative Strength Index)*

🎯 *What it shows:* If stock is overbought or oversold
📊 *How to read:*
• RSI > 70 = Overbought (might fall) 📉
• RSI < 30 = Oversold (might rise) 📈

💡 *Upgrade to GridWorks PRO* for live RSI charts!

_LITE users get education, PRO users get live data_ 🚀"""
        
        else:
            return self._get_indicator_help()
    
    def _extract_symbol(self, message: str) -> Optional[str]:
        """Extract stock symbol from message."""
        message_lower = message.lower()
        
        symbol_map = {
            "reliance": "RELIANCE",
            "tcs": "TCS",
            "hdfc": "HDFC", 
            "infosys": "INFY",
            "infy": "INFY",
            "itc": "ITC"
        }
        
        for key, symbol in symbol_map.items():
            if key in message_lower:
                return symbol
        
        return None
    
    def _get_chart_help(self) -> str:
        """Get help message for chart commands."""
        return """📊 *GridWorks LITE Charts*

🎯 *What you can do:*
• "Show [stock] chart" - Basic price chart
• "Set alert [stock] at [price]" - Price notifications  
• "RSI explanation" - Learn indicators

💡 *Available stocks:*
RELIANCE, TCS, HDFC, INFY, ITC

🚀 *Want advanced charts?*
Upgrade to GridWorks PRO for:
• Professional charting tools
• Real-time indicators  
• Pattern recognition
• Drawing tools

Type "upgrade to pro" to learn more!"""
    
    def _get_indicator_help(self) -> str:
        """Get help message for indicators."""
        return """📈 *GridWorks LITE Indicators*

🎯 *Learn about indicators:*
• "SMA explanation" - Moving averages
• "RSI explanation" - Overbought/oversold
• "MACD explanation" - Trend changes

💡 *LITE Features:*
✅ Indicator explanations
✅ Basic chart summaries
✅ Price alerts

🚀 *PRO Features:*
🔒 Live indicator charts
🔒 Advanced technical analysis
🔒 Pattern recognition
🔒 Drawing tools

Type "upgrade to pro" for advanced features!"""


# Demo usage
async def demo_lite_charting():
    """Demonstrate GridWorks LITE charting capabilities."""
    print("📊 Starting GridWorks LITE Charting Demo...")
    
    # Initialize LITE charting engine
    lite_engine = BasicChartingEngine()
    lite_messaging = LiteChartMessaging(lite_engine)
    
    # Create basic chart
    print("\\n📈 Creating basic chart for LITE user...")
    chart_id = await lite_engine.create_lite_chart("lite_user_123", "RELIANCE")
    print(f"✅ LITE chart created: {chart_id}")
    
    # Generate WhatsApp summary
    print("\\n📱 Generating WhatsApp chart summary...")
    summary = await lite_engine.generate_whatsapp_chart_summary(chart_id)
    print("📊 WhatsApp Summary:")
    print(summary)
    
    # Calculate basic indicators
    print("\\n📈 Calculating basic indicators...")
    sma = await lite_engine.get_basic_indicators(chart_id, LiteIndicator.SMA)
    print(f"✅ {sma.name}: {len(sma.values)} values calculated")
    
    rsi = await lite_engine.get_basic_indicators(chart_id, LiteIndicator.RSI)
    print(f"✅ {rsi.name}: {len(rsi.values)} values calculated")
    
    # Set price alert
    print("\\n🚨 Setting price alert...")
    alert_id = await lite_engine.set_price_alert("lite_user_123", "RELIANCE", 2600.0, "above")
    print(f"✅ Price alert set: {alert_id}")
    
    # Test messaging interface
    print("\\n💬 Testing WhatsApp messaging interface...")
    
    messages = [
        "Show Reliance chart",
        "Set alert TCS above 3200", 
        "RSI explanation please",
        "What indicators can I use?"
    ]
    
    for message in messages:
        print(f"\\n👤 User: {message}")
        response = await lite_messaging.process_chart_request("lite_user_123", message)
        print(f"🤖 GridWorks: {response[:100]}...")
    
    print("\\n🎯 LITE Charting Features Summary:")
    print("   📊 Basic candlestick charts")
    print("   📈 5 essential indicators")
    print("   🚨 Simple price alerts")
    print("   📱 WhatsApp chart summaries")
    print("   💡 Educational indicator explanations")
    print("   🎯 Upgrade prompts to PRO features")
    
    print("\\n✅ GridWorks LITE Charting Demo Complete!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_lite_charting())