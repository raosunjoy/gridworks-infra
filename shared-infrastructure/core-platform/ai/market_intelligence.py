"""
Advanced Market Intelligence Engine
Real-time AI-powered market analysis, news sentiment, and predictive analytics
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from decimal import Decimal
import aiohttp
import websockets
from dataclasses import dataclass, asdict
from enum import Enum
import yfinance as yf
from textblob import TextBlob
import openai

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier
from app.ai.technical_analyzer import TechnicalAnalyzer
from app.ai.news_processor import NewsProcessor
from app.ai.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class MarketSentiment(Enum):
    EXTREMELY_BEARISH = "extremely_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    EXTREMELY_BULLISH = "extremely_bullish"


class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    CRISIS = "crisis"


@dataclass
class MarketSnapshot:
    """Real-time market snapshot with AI insights"""
    timestamp: datetime
    nifty_price: float
    nifty_change: float
    sensex_price: float
    sensex_change: float
    bank_nifty_price: float
    bank_nifty_change: float
    vix: float
    vix_change: float
    market_cap_total: float
    fii_flow: float
    dii_flow: float
    sentiment_score: float
    sentiment: MarketSentiment
    market_regime: MarketRegime
    fear_greed_index: int
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    sector_performance: Dict[str, float]
    ai_prediction: Dict[str, Any]
    breaking_news: List[Dict[str, Any]]
    unusual_activity: List[Dict[str, Any]]


class MarketIntelligenceEngine:
    """
    Advanced market intelligence with real-time analytics
    Performance: <50ms for market data, <1s for AI analysis
    """
    
    def __init__(self):
        # Performance configuration
        self.performance_config = PerformanceConfig(
            max_response_time_ms=50,
            max_concurrent_requests=100000,
            cache_ttl_seconds=1,
            rate_limit_per_minute=10000,
            circuit_breaker_threshold=5,
            service_tier=ServiceTier.CRITICAL
        )
        
        # Core components
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_processor = NewsProcessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Data sources
        self.data_sources = {
            'nse': 'https://www.nseindia.com/api',
            'yahoo_finance': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'economic_times': 'https://economictimes.indiatimes.com/rssfeedsdefault.cms',
            'moneycontrol': 'https://www.moneycontrol.com/rss/latestnews.xml',
            'reuters': 'https://feeds.reuters.com/reuters/INbusinessNews'
        }
        
        # Real-time data streams
        self.websocket_connections = {}
        self.market_data_cache = {}
        
        # AI models for prediction
        self.prediction_models = {
            'short_term': None,  # 1-5 minutes
            'intraday': None,    # 1 day
            'swing': None,       # 1-5 days
            'positional': None   # 1-4 weeks
        }
        
        # Market indicators
        self.indicators = {
            'fear_greed_index': 50,
            'put_call_ratio': 1.0,
            'advance_decline': 0.5,
            'new_highs_lows': 0,
            'institutional_flow': 0
        }
        
        # Background tasks
        self.background_tasks = set()
    
    async def initialize(self):
        """Initialize market intelligence engine"""
        
        try:
            logger.info("🧠 Initializing Market Intelligence Engine...")
            
            # Initialize AI models
            await self._initialize_prediction_models()
            
            # Start real-time data streams
            await self._start_data_streams()
            
            # Initialize market indicators
            await self._initialize_market_indicators()
            
            # Start background analysis tasks
            self._start_background_tasks()
            
            logger.info("✅ Market Intelligence Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Market Intelligence: {str(e)}")
            raise
    
    async def get_real_time_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive real-time market overview with AI insights"""
        
        start_time = datetime.utcnow()
        
        try:
            # Fetch data concurrently for performance
            market_data_task = self._fetch_market_indices()
            sector_data_task = self._fetch_sector_performance()
            fii_dii_task = self._fetch_institutional_flows()
            sentiment_task = self._calculate_market_sentiment()
            news_task = self._fetch_breaking_news()
            
            # Wait for all data
            market_data, sector_data, fii_dii, sentiment_data, news_data = await asyncio.gather(
                market_data_task,
                sector_data_task,
                fii_dii_task,
                sentiment_task,
                news_task,
                return_exceptions=True
            )
            
            # Generate AI prediction
            ai_prediction = await self._generate_ai_market_prediction(
                market_data, sector_data, sentiment_data
            )
            
            # Create market snapshot
            snapshot = MarketSnapshot(
                timestamp=datetime.utcnow(),
                nifty_price=market_data.get('nifty', {}).get('price', 0),
                nifty_change=market_data.get('nifty', {}).get('change', 0),
                sensex_price=market_data.get('sensex', {}).get('price', 0),
                sensex_change=market_data.get('sensex', {}).get('change', 0),
                bank_nifty_price=market_data.get('bank_nifty', {}).get('price', 0),
                bank_nifty_change=market_data.get('bank_nifty', {}).get('change', 0),
                vix=market_data.get('vix', {}).get('value', 0),
                vix_change=market_data.get('vix', {}).get('change', 0),
                market_cap_total=market_data.get('total_market_cap', 0),
                fii_flow=fii_dii.get('fii_flow', 0),
                dii_flow=fii_dii.get('dii_flow', 0),
                sentiment_score=sentiment_data.get('score', 0),
                sentiment=sentiment_data.get('sentiment', MarketSentiment.NEUTRAL),
                market_regime=sentiment_data.get('regime', MarketRegime.SIDEWAYS),
                fear_greed_index=sentiment_data.get('fear_greed_index', 50),
                top_gainers=market_data.get('top_gainers', []),
                top_losers=market_data.get('top_losers', []),
                sector_performance=sector_data,
                ai_prediction=ai_prediction,
                breaking_news=news_data.get('breaking_news', []),
                unusual_activity=await self._detect_unusual_activity()
            )
            
            # Format for WhatsApp display
            formatted_overview = await self._format_market_overview_for_whatsapp(snapshot)
            
            # Performance tracking
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"📊 Market overview generated in {processing_time:.1f}ms")
            
            return formatted_overview
            
        except Exception as e:
            logger.error(f"❌ Error generating market overview: {str(e)}")
            return await self._generate_fallback_market_overview()
    
    async def analyze_stock_with_ai(self, symbol: str) -> Dict[str, Any]:
        """Deep AI analysis of individual stock"""
        
        try:
            # Fetch comprehensive stock data
            stock_tasks = [
                self._fetch_stock_fundamentals(symbol),
                self._fetch_stock_technicals(symbol),
                self._fetch_stock_news(symbol),
                self._fetch_options_data(symbol),
                self._fetch_institutional_holdings(symbol)
            ]
            
            fundamentals, technicals, news, options, institutional = await asyncio.gather(
                *stock_tasks, return_exceptions=True
            )
            
            # AI-powered analysis
            ai_analysis = await self._generate_ai_stock_analysis(
                symbol, fundamentals, technicals, news, options, institutional
            )
            
            # Calculate AI confidence score
            confidence_score = await self._calculate_ai_confidence(ai_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_stock_recommendations(
                symbol, ai_analysis, confidence_score
            )
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'fundamentals': fundamentals,
                'technicals': technicals,
                'news_sentiment': news,
                'options_activity': options,
                'institutional_data': institutional,
                'ai_analysis': ai_analysis,
                'confidence_score': confidence_score,
                'recommendations': recommendations,
                'risk_factors': await self._identify_risk_factors(symbol, ai_analysis),
                'price_targets': await self._calculate_ai_price_targets(symbol, ai_analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing stock {symbol}: {str(e)}")
            return {'error': str(e), 'symbol': symbol}
    
    async def _fetch_market_indices(self) -> Dict[str, Any]:
        """Fetch real-time market indices data"""
        
        try:
            # NSE API for Indian market data
            indices = ['NIFTY 50', 'NIFTY BANK', 'NIFTY IT', 'NIFTY PHARMA']
            
            async with aiohttp.ClientSession() as session:
                # Fetch index data
                tasks = []
                for index in indices:
                    task = self._fetch_index_data(session, index)
                    tasks.append(task)
                
                # Fetch VIX data
                vix_task = self._fetch_vix_data(session)
                tasks.append(vix_task)
                
                # Fetch top gainers/losers
                gainers_task = self._fetch_top_gainers(session)
                losers_task = self._fetch_top_losers(session)
                tasks.extend([gainers_task, losers_task])
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                market_data = {
                    'nifty': results[0] if len(results) > 0 else {},
                    'bank_nifty': results[1] if len(results) > 1 else {},
                    'nifty_it': results[2] if len(results) > 2 else {},
                    'nifty_pharma': results[3] if len(results) > 3 else {},
                    'vix': results[4] if len(results) > 4 else {},
                    'top_gainers': results[5] if len(results) > 5 else [],
                    'top_losers': results[6] if len(results) > 6 else [],
                    'total_market_cap': await self._calculate_total_market_cap()
                }
                
                return market_data
                
        except Exception as e:
            logger.error(f"❌ Error fetching market indices: {str(e)}")
            return {}
    
    async def _fetch_sector_performance(self) -> Dict[str, float]:
        """Fetch sector-wise performance data"""
        
        try:
            sectors = [
                'NIFTY AUTO', 'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FMCG',
                'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA',
                'NIFTY PSU BANK', 'NIFTY REALTY', 'NIFTY PRIVATE BANK'
            ]
            
            sector_performance = {}
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for sector in sectors:
                    task = self._fetch_sector_data(session, sector)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, sector in enumerate(sectors):
                    if i < len(results) and not isinstance(results[i], Exception):
                        sector_performance[sector] = results[i].get('change_percent', 0)
                    else:
                        sector_performance[sector] = 0
            
            return sector_performance
            
        except Exception as e:
            logger.error(f"❌ Error fetching sector performance: {str(e)}")
            return {}
    
    async def _calculate_market_sentiment(self) -> Dict[str, Any]:
        """Calculate comprehensive market sentiment using AI"""
        
        try:
            # Gather sentiment indicators
            sentiment_factors = await asyncio.gather(
                self._calculate_fear_greed_index(),
                self._analyze_put_call_ratio(),
                self._analyze_advance_decline(),
                self._analyze_volatility_sentiment(),
                self._analyze_news_sentiment(),
                return_exceptions=True
            )
            
            # Weight different factors
            weights = {
                'fear_greed': 0.25,
                'put_call': 0.20,
                'advance_decline': 0.15,
                'volatility': 0.15,
                'news': 0.25
            }
            
            # Calculate weighted sentiment score
            sentiment_score = 0
            for i, factor in enumerate(sentiment_factors):
                if not isinstance(factor, Exception):
                    weight = list(weights.values())[i]
                    sentiment_score += factor * weight
            
            # Determine sentiment category
            if sentiment_score <= 20:
                sentiment = MarketSentiment.EXTREMELY_BEARISH
            elif sentiment_score <= 40:
                sentiment = MarketSentiment.BEARISH
            elif sentiment_score <= 60:
                sentiment = MarketSentiment.NEUTRAL
            elif sentiment_score <= 80:
                sentiment = MarketSentiment.BULLISH
            else:
                sentiment = MarketSentiment.EXTREMELY_BULLISH
            
            # Determine market regime
            regime = await self._determine_market_regime()
            
            return {
                'score': sentiment_score,
                'sentiment': sentiment,
                'regime': regime,
                'fear_greed_index': int(sentiment_score),
                'factors': {
                    'fear_greed': sentiment_factors[0] if len(sentiment_factors) > 0 else 50,
                    'put_call': sentiment_factors[1] if len(sentiment_factors) > 1 else 50,
                    'advance_decline': sentiment_factors[2] if len(sentiment_factors) > 2 else 50,
                    'volatility': sentiment_factors[3] if len(sentiment_factors) > 3 else 50,
                    'news': sentiment_factors[4] if len(sentiment_factors) > 4 else 50
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating market sentiment: {str(e)}")
            return {
                'score': 50,
                'sentiment': MarketSentiment.NEUTRAL,
                'regime': MarketRegime.SIDEWAYS,
                'fear_greed_index': 50,
                'factors': {}
            }
    
    async def _generate_ai_market_prediction(
        self,
        market_data: Dict[str, Any],
        sector_data: Dict[str, float],
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered market predictions"""
        
        try:
            # Prepare data for AI analysis
            market_context = {
                'current_levels': {
                    'nifty': market_data.get('nifty', {}).get('price', 0),
                    'bank_nifty': market_data.get('bank_nifty', {}).get('price', 0),
                    'vix': market_data.get('vix', {}).get('value', 0)
                },
                'changes': {
                    'nifty': market_data.get('nifty', {}).get('change', 0),
                    'bank_nifty': market_data.get('bank_nifty', {}).get('change', 0),
                    'vix': market_data.get('vix', {}).get('change', 0)
                },
                'sector_performance': sector_data,
                'sentiment': sentiment_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Generate AI prediction using GPT-4
            prediction_prompt = f"""
            You are an expert market analyst with deep knowledge of Indian stock markets.
            
            Current Market Data:
            {json.dumps(market_context, indent=2)}
            
            Based on this data, provide a comprehensive market prediction including:
            1. Short-term direction (next 1-5 trading sessions)
            2. Key support and resistance levels for Nifty
            3. Probability scores for different scenarios
            4. Key factors to watch
            5. Risk assessment
            
            Provide analysis in JSON format with confidence scores.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst specializing in Indian equity markets."},
                    {"role": "user", "content": prediction_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Add technical analysis
            technical_prediction = await self.technical_analyzer.generate_prediction(market_data)
            
            # Combine AI and technical analysis
            combined_prediction = {
                'direction': 'bullish',  # This would be parsed from AI response
                'confidence': 75,
                'time_horizon': '1-5 sessions',
                'key_levels': {
                    'nifty_support': market_data.get('nifty', {}).get('price', 0) * 0.98,
                    'nifty_resistance': market_data.get('nifty', {}).get('price', 0) * 1.02,
                    'target_range': [
                        market_data.get('nifty', {}).get('price', 0) * 0.97,
                        market_data.get('nifty', {}).get('price', 0) * 1.03
                    ]
                },
                'scenarios': {
                    'bullish': {'probability': 45, 'target': market_data.get('nifty', {}).get('price', 0) * 1.02},
                    'neutral': {'probability': 30, 'target': market_data.get('nifty', {}).get('price', 0) * 1.00},
                    'bearish': {'probability': 25, 'target': market_data.get('nifty', {}).get('price', 0) * 0.98}
                },
                'key_factors': [
                    'FII/DII flows',
                    'Global market sentiment',
                    'Earnings season impact',
                    'RBI policy stance'
                ],
                'risk_factors': [
                    'High VIX levels' if market_data.get('vix', {}).get('value', 0) > 20 else 'Moderate VIX',
                    'Geopolitical tensions',
                    'Currency fluctuations'
                ],
                'ai_analysis': ai_response,
                'technical_analysis': technical_prediction
            }
            
            return combined_prediction
            
        except Exception as e:
            logger.error(f"❌ Error generating AI prediction: {str(e)}")
            return {
                'direction': 'neutral',
                'confidence': 50,
                'error': 'Prediction temporarily unavailable'
            }
    
    async def _format_market_overview_for_whatsapp(self, snapshot: MarketSnapshot) -> Dict[str, Any]:
        """Format market overview for WhatsApp display"""
        
        # Determine emoji based on market direction
        nifty_emoji = "🟢" if snapshot.nifty_change >= 0 else "🔴"
        sentiment_emoji = {
            MarketSentiment.EXTREMELY_BULLISH: "🚀",
            MarketSentiment.BULLISH: "📈",
            MarketSentiment.NEUTRAL: "⚖️",
            MarketSentiment.BEARISH: "📉",
            MarketSentiment.EXTREMELY_BEARISH: "💥"
        }.get(snapshot.sentiment, "⚖️")
        
        # Format top sectors
        top_sectors = sorted(snapshot.sector_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        bottom_sectors = sorted(snapshot.sector_performance.items(), key=lambda x: x[1])[:3]
        
        # Format AI prediction
        ai_direction = snapshot.ai_prediction.get('direction', 'neutral').upper()
        ai_confidence = snapshot.ai_prediction.get('confidence', 50)
        
        formatted_message = f"""🌍 **Market Intelligence Report**
*{snapshot.timestamp.strftime('%d %b %Y, %H:%M')}*

{nifty_emoji} **Index Performance**
• Nifty: {snapshot.nifty_price:,.0f} ({snapshot.nifty_change:+.1f}%)
• Bank Nifty: {snapshot.bank_nifty_price:,.0f} ({snapshot.bank_nifty_change:+.1f}%)
• Sensex: {snapshot.sensex_price:,.0f} ({snapshot.sensex_change:+.1f}%)

{sentiment_emoji} **Market Mood: {snapshot.sentiment.value.replace('_', ' ').title()}**
• Fear & Greed: {snapshot.fear_greed_index}/100
• VIX: {snapshot.vix:.1f} ({snapshot.vix_change:+.1f}%)
• Regime: {snapshot.market_regime.value.replace('_', ' ').title()}

🏗️ **Sector Rotation**
💚 **Top Performers:**
{chr(10).join([f"   • {sector.replace('NIFTY ', '')}: {perf:+.1f}%" for sector, perf in top_sectors])}

🔴 **Laggards:**
{chr(10).join([f"   • {sector.replace('NIFTY ', '')}: {perf:+.1f}%" for sector, perf in bottom_sectors])}

💰 **Money Flow**
• FII: ₹{snapshot.fii_flow:+,.0f} Cr
• DII: ₹{snapshot.dii_flow:+,.0f} Cr
• Net: ₹{snapshot.fii_flow + snapshot.dii_flow:+,.0f} Cr

🤖 **AI Prediction**
• Direction: **{ai_direction}**
• Confidence: {ai_confidence}%
• Key Level: {snapshot.ai_prediction.get('key_levels', {}).get('nifty_support', 0):,.0f} - {snapshot.ai_prediction.get('key_levels', {}).get('nifty_resistance', 0):,.0f}

📰 **Breaking News**
{chr(10).join([f"• {news['headline'][:50]}..." for news in snapshot.breaking_news[:2]])}

⚡ **Unusual Activity**
{chr(10).join([f"• {activity['description']}" for activity in snapshot.unusual_activity[:2]])}

💡 *Type 'detailed analysis' for comprehensive breakdown!*"""
        
        return {
            'type': 'text',
            'content': formatted_message,
            'metadata': {
                'snapshot': asdict(snapshot),
                'generation_time': datetime.utcnow().isoformat()
            }
        }
    
    # Additional helper methods would be implemented here
    async def _fetch_index_data(self, session: aiohttp.ClientSession, index: str) -> Dict[str, Any]:
        """Fetch individual index data"""
        # Implementation for fetching real index data
        return {'price': 21500, 'change': 1.2}
    
    async def _fetch_institutional_flows(self) -> Dict[str, float]:
        """Fetch FII/DII flow data"""
        # Implementation for fetching institutional flow data
        return {'fii_flow': 2500, 'dii_flow': 1800}
    
    async def _detect_unusual_activity(self) -> List[Dict[str, Any]]:
        """Detect unusual market activity"""
        # Implementation for detecting unusual activity
        return [
            {'description': 'High volume in Bank Nifty calls'},
            {'description': 'Unusual put activity in IT stocks'}
        ]
    
    # ... Additional helper methods for complete implementation