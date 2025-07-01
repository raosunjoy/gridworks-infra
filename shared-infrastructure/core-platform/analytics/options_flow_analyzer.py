"""
Options Flow Analyzer
====================

Detects unusual options activity, dark pool flows, and institutional patterns
for retail traders to identify potential opportunities and market movements.

Features:
- Real-time options flow monitoring
- Unusual activity detection (volume, OI changes)
- Dark pool flow analysis
- Institutional pattern recognition
- Risk assessment and alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class FlowType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNUSUAL = "UNUSUAL"


class AlertSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class OptionsContract:
    symbol: str
    strike: float
    expiry: datetime
    option_type: str  # "CALL" or "PUT"
    last_price: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FlowDetection:
    symbol: str
    flow_type: FlowType
    severity: AlertSeverity
    volume: int
    value: float
    unusual_factor: float
    description: str
    contracts: List[OptionsContract]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DarkPoolFlow:
    symbol: str
    estimated_size: float
    direction: str  # "BUY" or "SELL"
    confidence: float
    price_level: float
    timestamp: datetime = field(default_factory=datetime.now)


class OptionsFlowAnalyzer:
    """Advanced options flow analysis with unusual activity detection."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.historical_data = defaultdict(deque)
        self.flow_history = deque(maxlen=1000)
        self.dark_pool_history = deque(maxlen=500)
        self.alert_history = deque(maxlen=200)
        self.running = False
        
        # Analysis parameters
        self.volume_threshold_multiplier = 3.0
        self.oi_change_threshold = 0.2
        self.unusual_iv_threshold = 0.3
        self.dark_pool_size_threshold = 1000000  # $1M+
        
    def _default_config(self) -> Dict:
        return {
            "scan_interval": 5,  # seconds
            "lookback_days": 30,
            "min_volume": 100,
            "min_value": 50000,  # $50K minimum
            "max_symbols": 500,
            "enable_dark_pool": True,
            "enable_institutional": True,
            "risk_free_rate": 0.05
        }
    
    async def start_monitoring(self):
        """Start real-time options flow monitoring."""
        self.running = True
        logger.info("🔄 Options Flow Analyzer started")
        
        while self.running:
            try:
                await self._scan_options_flow()
                await asyncio.sleep(self.config["scan_interval"])
            except Exception as e:
                logger.error(f"❌ Flow monitoring error: {e}")
                await asyncio.sleep(10)
    
    def stop_monitoring(self):
        """Stop options flow monitoring."""
        self.running = False
        logger.info("⏹️ Options Flow Analyzer stopped")
    
    async def _scan_options_flow(self):
        """Scan for unusual options activity."""
        try:
            # Get current options data (simulated for demo)
            options_data = await self._fetch_options_data()
            
            for symbol, contracts in options_data.items():
                # Analyze unusual volume
                volume_alerts = self._detect_unusual_volume(symbol, contracts)
                
                # Analyze unusual open interest changes
                oi_alerts = self._detect_unusual_oi(symbol, contracts)
                
                # Analyze implied volatility spikes
                iv_alerts = self._detect_iv_anomalies(symbol, contracts)
                
                # Detect potential sweeps
                sweep_alerts = self._detect_option_sweeps(symbol, contracts)
                
                # Combine all alerts
                all_alerts = volume_alerts + oi_alerts + iv_alerts + sweep_alerts
                
                for alert in all_alerts:
                    self.alert_history.append(alert)
                    await self._process_alert(alert)
                
                # Dark pool analysis
                if self.config["enable_dark_pool"]:
                    dark_flows = await self._analyze_dark_pool_activity(symbol, contracts)
                    self.dark_pool_history.extend(dark_flows)
            
        except Exception as e:
            logger.error(f"❌ Options flow scan error: {e}")
    
    def _detect_unusual_volume(self, symbol: str, contracts: List[OptionsContract]) -> List[FlowDetection]:
        """Detect unusual volume spikes."""
        alerts = []
        
        for contract in contracts:
            # Get historical average volume
            historical_avg = self._get_historical_average_volume(symbol, contract)
            
            if historical_avg > 0:
                volume_ratio = contract.volume / historical_avg
                
                if volume_ratio >= self.volume_threshold_multiplier:
                    severity = self._calculate_severity(volume_ratio)
                    
                    flow_type = FlowType.BULLISH if contract.option_type == "CALL" else FlowType.BEARISH
                    if volume_ratio > 10:
                        flow_type = FlowType.UNUSUAL
                    
                    alert = FlowDetection(
                        symbol=symbol,
                        flow_type=flow_type,
                        severity=severity,
                        volume=contract.volume,
                        value=contract.volume * contract.last_price * 100,
                        unusual_factor=volume_ratio,
                        description=f"Volume spike: {volume_ratio:.1f}x normal ({contract.volume:,} vs {historical_avg:.0f} avg)",
                        contracts=[contract],
                        confidence=min(0.95, volume_ratio / 20)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_unusual_oi(self, symbol: str, contracts: List[OptionsContract]) -> List[FlowDetection]:
        """Detect unusual open interest changes."""
        alerts = []
        
        for contract in contracts:
            # Get previous day's OI
            prev_oi = self._get_previous_oi(symbol, contract)
            
            if prev_oi > 0:
                oi_change = (contract.open_interest - prev_oi) / prev_oi
                
                if abs(oi_change) >= self.oi_change_threshold:
                    severity = AlertSeverity.MEDIUM if abs(oi_change) < 0.5 else AlertSeverity.HIGH
                    
                    flow_type = FlowType.BULLISH if oi_change > 0 and contract.option_type == "CALL" else FlowType.BEARISH
                    
                    alert = FlowDetection(
                        symbol=symbol,
                        flow_type=flow_type,
                        severity=severity,
                        volume=contract.volume,
                        value=abs(oi_change) * contract.last_price * 100,
                        unusual_factor=abs(oi_change),
                        description=f"OI change: {oi_change:+.1%} ({contract.open_interest:,} vs {prev_oi:,})",
                        contracts=[contract],
                        confidence=min(0.9, abs(oi_change) * 2)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_iv_anomalies(self, symbol: str, contracts: List[OptionsContract]) -> List[FlowDetection]:
        """Detect implied volatility anomalies."""
        alerts = []
        
        for contract in contracts:
            # Get historical IV average
            historical_iv = self._get_historical_iv(symbol, contract)
            
            if historical_iv > 0:
                iv_change = (contract.implied_volatility - historical_iv) / historical_iv
                
                if abs(iv_change) >= self.unusual_iv_threshold:
                    severity = AlertSeverity.MEDIUM if abs(iv_change) < 0.6 else AlertSeverity.HIGH
                    
                    flow_type = FlowType.UNUSUAL
                    
                    alert = FlowDetection(
                        symbol=symbol,
                        flow_type=flow_type,
                        severity=severity,
                        volume=contract.volume,
                        value=contract.volume * contract.last_price * 100,
                        unusual_factor=abs(iv_change),
                        description=f"IV spike: {iv_change:+.1%} ({contract.implied_volatility:.2f} vs {historical_iv:.2f} avg)",
                        contracts=[contract],
                        confidence=min(0.85, abs(iv_change) * 1.5)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_option_sweeps(self, symbol: str, contracts: List[OptionsContract]) -> List[FlowDetection]:
        """Detect potential option sweeps (large market orders)."""
        alerts = []
        
        # Group by strike and expiry
        strikes = defaultdict(list)
        for contract in contracts:
            key = (contract.strike, contract.expiry, contract.option_type)
            strikes[key].append(contract)
        
        for key, strike_contracts in strikes.items():
            total_volume = sum(c.volume for c in strike_contracts)
            total_value = sum(c.volume * c.last_price * 100 for c in strike_contracts)
            
            if total_value >= self.config["min_value"] * 5:  # 5x minimum for sweep detection
                avg_volume = self._get_average_volume_for_strike(symbol, key)
                
                if avg_volume > 0 and total_volume / avg_volume >= 2.0:
                    severity = AlertSeverity.HIGH if total_value > 500000 else AlertSeverity.MEDIUM
                    
                    flow_type = FlowType.BULLISH if key[2] == "CALL" else FlowType.BEARISH
                    
                    alert = FlowDetection(
                        symbol=symbol,
                        flow_type=flow_type,
                        severity=severity,
                        volume=total_volume,
                        value=total_value,
                        unusual_factor=total_volume / avg_volume,
                        description=f"Potential sweep: ${total_value:,.0f} across {len(strike_contracts)} contracts",
                        contracts=strike_contracts,
                        confidence=0.8
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _analyze_dark_pool_activity(self, symbol: str, contracts: List[OptionsContract]) -> List[DarkPoolFlow]:
        """Analyze potential dark pool activity."""
        dark_flows = []
        
        # Analyze price action vs options flow
        for contract in contracts:
            # Check for price-flow divergence (simplified)
            if contract.volume > 1000 and contract.last_price > 0:
                estimated_size = contract.volume * contract.last_price * 100
                
                if estimated_size >= self.dark_pool_size_threshold:
                    # Determine direction based on delta and flow
                    direction = "BUY" if contract.delta > 0.5 else "SELL"
                    confidence = min(0.7, estimated_size / 5000000)  # Max confidence at $5M
                    
                    dark_flow = DarkPoolFlow(
                        symbol=symbol,
                        estimated_size=estimated_size,
                        direction=direction,
                        confidence=confidence,
                        price_level=contract.strike
                    )
                    dark_flows.append(dark_flow)
        
        return dark_flows
    
    async def _process_alert(self, alert: FlowDetection):
        """Process and potentially send alert."""
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            logger.info(f"🚨 {alert.severity.value} Alert: {alert.symbol} - {alert.description}")
            # Here you would integrate with notification system
    
    def _calculate_severity(self, unusual_factor: float) -> AlertSeverity:
        """Calculate alert severity based on unusual factor."""
        if unusual_factor >= 20:
            return AlertSeverity.CRITICAL
        elif unusual_factor >= 10:
            return AlertSeverity.HIGH
        elif unusual_factor >= 5:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _get_historical_average_volume(self, symbol: str, contract: OptionsContract) -> float:
        """Get historical average volume for a contract (simplified)."""
        # In real implementation, this would query historical database
        # For demo, return simulated historical average
        return max(100, contract.volume * 0.3 + np.random.normal(200, 50))
    
    def _get_previous_oi(self, symbol: str, contract: OptionsContract) -> int:
        """Get previous day's open interest (simplified)."""
        # In real implementation, this would query historical database
        return max(0, int(contract.open_interest * 0.95 + np.random.normal(0, contract.open_interest * 0.1)))
    
    def _get_historical_iv(self, symbol: str, contract: OptionsContract) -> float:
        """Get historical implied volatility average (simplified)."""
        # In real implementation, this would query historical database
        return max(0.1, contract.implied_volatility * 0.9 + np.random.normal(0, 0.05))
    
    def _get_average_volume_for_strike(self, symbol: str, key: Tuple) -> float:
        """Get average volume for specific strike/expiry combination."""
        # Simplified implementation
        return 500 + np.random.normal(200, 100)
    
    async def _fetch_options_data(self) -> Dict[str, List[OptionsContract]]:
        """Fetch current options data (simulated for demo)."""
        # In real implementation, this would connect to options data feed
        # Simulated data for demonstration
        symbols = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS", "INFY"]
        options_data = {}
        
        for symbol in symbols:
            contracts = []
            base_price = 100 + np.random.normal(0, 20)
            
            # Generate sample contracts
            for i in range(5):
                strike = base_price + (i - 2) * 10
                for option_type in ["CALL", "PUT"]:
                    contract = OptionsContract(
                        symbol=symbol,
                        strike=strike,
                        expiry=datetime.now() + timedelta(days=7 + i * 7),
                        option_type=option_type,
                        last_price=max(0.1, np.random.normal(5, 2)),
                        volume=max(0, int(np.random.exponential(500))),
                        open_interest=max(0, int(np.random.exponential(1000))),
                        implied_volatility=max(0.1, np.random.normal(0.25, 0.05)),
                        delta=np.random.uniform(0.1, 0.9),
                        gamma=np.random.uniform(0.01, 0.1),
                        theta=-np.random.uniform(0.01, 0.05),
                        vega=np.random.uniform(0.1, 0.5)
                    )
                    contracts.append(contract)
            
            options_data[symbol] = contracts
        
        return options_data
    
    def get_flow_summary(self, symbol: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get flow summary for the specified period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        relevant_flows = [
            flow for flow in self.alert_history
            if flow.timestamp >= cutoff_time and (symbol is None or flow.symbol == symbol)
        ]
        
        if not relevant_flows:
            return {"message": "No significant flows detected"}
        
        # Aggregate by symbol and flow type
        summary = defaultdict(lambda: {
            "total_volume": 0,
            "total_value": 0,
            "alerts": [],
            "avg_confidence": 0
        })
        
        for flow in relevant_flows:
            key = f"{flow.symbol}_{flow.flow_type.value}"
            summary[key]["total_volume"] += flow.volume
            summary[key]["total_value"] += flow.value
            summary[key]["alerts"].append({
                "severity": flow.severity.value,
                "description": flow.description,
                "confidence": flow.confidence,
                "timestamp": flow.timestamp.isoformat()
            })
        
        # Calculate averages
        for key, data in summary.items():
            if data["alerts"]:
                data["avg_confidence"] = sum(alert["confidence"] for alert in data["alerts"]) / len(data["alerts"])
        
        return dict(summary)
    
    def get_dark_pool_summary(self, symbol: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get dark pool activity summary."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        relevant_flows = [
            flow for flow in self.dark_pool_history
            if flow.timestamp >= cutoff_time and (symbol is None or flow.symbol == symbol)
        ]
        
        if not relevant_flows:
            return {"message": "No significant dark pool activity detected"}
        
        total_size = sum(flow.estimated_size for flow in relevant_flows)
        buy_flows = [f for f in relevant_flows if f.direction == "BUY"]
        sell_flows = [f for f in relevant_flows if f.direction == "SELL"]
        
        return {
            "total_estimated_size": total_size,
            "buy_size": sum(f.estimated_size for f in buy_flows),
            "sell_size": sum(f.estimated_size for f in sell_flows),
            "flow_count": len(relevant_flows),
            "avg_confidence": sum(f.confidence for f in relevant_flows) / len(relevant_flows) if relevant_flows else 0,
            "top_flows": [
                {
                    "symbol": f.symbol,
                    "size": f.estimated_size,
                    "direction": f.direction,
                    "confidence": f.confidence,
                    "timestamp": f.timestamp.isoformat()
                }
                for f in sorted(relevant_flows, key=lambda x: x.estimated_size, reverse=True)[:5]
            ]
        }


# Demo usage
async def demo_options_flow_analyzer():
    """Demonstrate the options flow analyzer."""
    analyzer = OptionsFlowAnalyzer()
    
    print("🔄 Starting Options Flow Analyzer Demo...")
    
    # Start monitoring in background
    monitor_task = asyncio.create_task(analyzer.start_monitoring())
    
    # Let it run for a bit
    await asyncio.sleep(30)
    
    # Get summaries
    print("\n📊 Flow Summary:")
    flow_summary = analyzer.get_flow_summary(hours=1)
    for key, data in flow_summary.items():
        print(f"  {key}: ${data['total_value']:,.0f} volume, {len(data['alerts'])} alerts")
    
    print("\n🌊 Dark Pool Summary:")
    dark_summary = analyzer.get_dark_pool_summary(hours=1)
    if "total_estimated_size" in dark_summary:
        print(f"  Total Size: ${dark_summary['total_estimated_size']:,.0f}")
        print(f"  Buy/Sell Ratio: {dark_summary['buy_size']/max(1, dark_summary['sell_size']):.2f}")
    
    # Stop monitoring
    analyzer.stop_monitoring()
    monitor_task.cancel()
    
    print("✅ Options Flow Analyzer Demo Complete")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_options_flow_analyzer())