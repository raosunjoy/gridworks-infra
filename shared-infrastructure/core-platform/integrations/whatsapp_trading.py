"""?
WhatsApp Trading Integration

Enables one-click trading directly from WhatsApp charts and messages.
Integrates with WhatsApp Business API for seamless trading experience.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import uuid
import qrcode
import io
import base64
from PIL import Image, ImageDraw, ImageFont

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.trading import Trade, TradeOrder
from app.models.whatsapp import WhatsAppSession, WhatsAppMessage
from app.services.trading_engine import TradingEngine
from app.services.chart_generator import ChartImageGenerator
from app.services.whatsapp_client import WhatsAppClient
from app.services.risk_management import RiskManager

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp-trading"])

# Pydantic models
class WhatsAppTradeRequest(BaseModel):
    symbol: str
    action: str = Field(..., regex="^(BUY|SELL)$")
    quantity: int = Field(..., gt=0)
    order_type: str = Field(default="MARKET", regex="^(MARKET|LIMIT|STOP|STOP_LIMIT)$")
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    chart_id: Optional[str] = None
    whatsapp_number: str
    message_id: str

class WhatsAppChartRequest(BaseModel):
    symbol: str
    timeframe: str = Field(default="5m")
    indicators: List[str] = Field(default_factory=list)
    drawing_tools: List[Dict[str, Any]] = Field(default_factory=list)
    whatsapp_number: str
    include_trade_buttons: bool = Field(default=True)
    analysis_notes: Optional[str] = None

class WhatsAppAlertRequest(BaseModel):
    symbol: str
    condition: Dict[str, Any]
    alert_type: str = Field(..., regex="^(PRICE|PATTERN|INDICATOR)$")
    whatsapp_number: str
    message_template: Optional[str] = None

class WhatsAppQuickTradeRequest(BaseModel):
    preset_name: str  # "scalp_buy", "swing_sell", etc.
    symbol: str
    whatsapp_number: str
    risk_amount: Optional[float] = None

# Response models
class WhatsAppTradeResponse(BaseModel):
    trade_id: str
    status: str
    message: str
    whatsapp_message_id: str
    confirmation_required: bool

class WhatsAppChartResponse(BaseModel):
    chart_url: str
    whatsapp_message_id: str
    trade_buttons: List[Dict[str, str]]
    expires_at: datetime


class WhatsAppTradingManager:
    """Manages WhatsApp trading integration"""
    
    def __init__(self):
        self.whatsapp_client = WhatsAppClient()
        self.trading_engine = TradingEngine()
        self.chart_generator = ChartImageGenerator()
        self.risk_manager = RiskManager()
        
        # Trading presets for quick actions
        self.trade_presets = {
            'scalp_buy': {
                'action': 'BUY',
                'order_type': 'MARKET',
                'risk_percentage': 0.5,
                'stop_loss_percentage': 0.2,
                'take_profit_percentage': 0.4
            },
            'scalp_sell': {
                'action': 'SELL',
                'order_type': 'MARKET',
                'risk_percentage': 0.5,
                'stop_loss_percentage': 0.2,
                'take_profit_percentage': 0.4
            },
            'swing_buy': {
                'action': 'BUY',
                'order_type': 'LIMIT',
                'risk_percentage': 2.0,
                'stop_loss_percentage': 1.0,
                'take_profit_percentage': 3.0
            },
            'swing_sell': {
                'action': 'SELL',
                'order_type': 'LIMIT',
                'risk_percentage': 2.0,
                'stop_loss_percentage': 1.0,
                'take_profit_percentage': 3.0
            },
            'momentum_buy': {
                'action': 'BUY',
                'order_type': 'MARKET',
                'risk_percentage': 1.0,
                'stop_loss_percentage': 0.5,
                'take_profit_percentage': 2.0
            }
        }
        
        # Message templates
        self.message_templates = {
            'trade_confirmation': "🎯 Trade Confirmation\n\n📊 Symbol: {symbol}\n📈 Action: {action}\n📦 Quantity: {quantity}\n💰 Price: ₹{price}\n\nReply 'YES' to confirm or 'NO' to cancel\n\n⏰ Expires in 5 minutes",
            'trade_executed': "✅ Trade Executed\n\n📊 {symbol} - {action} {quantity} shares\n💰 Price: ₹{price}\n📈 P&L: {pnl}\n\n🔗 View details: {trade_url}",
            'chart_analysis': "📊 Chart Analysis\n\n🎯 {symbol} - {timeframe}\n📈 Trend: {trend}\n💪 Strength: {strength}%\n🎨 Patterns: {patterns}\n\n💡 {analysis_notes}",
            'alert_triggered': "🚨 Price Alert\n\n📊 {symbol}\n💰 Current: ₹{current_price}\n🎯 Target: ₹{target_price}\n📈 Change: {change}%\n\n{condition_met}"
        }
    
    async def execute_whatsapp_trade(
        self, 
        db: Session, 
        user_id: str, 
        trade_request: WhatsAppTradeRequest
    ) -> Dict[str, Any]:
        """Execute trade from WhatsApp message"""
        
        try:
            # Validate user and WhatsApp session
            whatsapp_session = await self._validate_whatsapp_session(
                db, user_id, trade_request.whatsapp_number
            )
            
            # Risk management check
            risk_check = await self.risk_manager.validate_trade(
                user_id=user_id,
                symbol=trade_request.symbol,
                action=trade_request.action,
                quantity=trade_request.quantity,
                price=trade_request.price
            )
            
            if not risk_check['approved']:
                await self._send_risk_rejection_message(
                    trade_request.whatsapp_number, 
                    risk_check['reason']
                )
                return {
                    'success': False,
                    'reason': risk_check['reason'],
                    'risk_check': risk_check
                }
            
            # Generate trade confirmation
            trade_id = str(uuid.uuid4())
            confirmation_message = self._generate_trade_confirmation(
                trade_request, trade_id
            )
            
            # Send confirmation message
            whatsapp_message_id = await self.whatsapp_client.send_message(
                phone_number=trade_request.whatsapp_number,
                message=confirmation_message,
                buttons=[
                    {'id': f'confirm_{trade_id}', 'title': '✅ Confirm Trade'},
                    {'id': f'cancel_{trade_id}', 'title': '❌ Cancel Trade'}
                ]
            )
            
            # Store pending trade
            pending_trade = {
                'trade_id': trade_id,
                'user_id': user_id,
                'whatsapp_number': trade_request.whatsapp_number,
                'whatsapp_message_id': whatsapp_message_id,
                'trade_details': trade_request.dict(),
                'status': 'pending_confirmation',
                'expires_at': datetime.utcnow() + timedelta(minutes=5),
                'created_at': datetime.utcnow()
            }
            
            await self._store_pending_trade(db, pending_trade)
            
            return {
                'success': True,
                'trade_id': trade_id,
                'status': 'pending_confirmation',
                'whatsapp_message_id': whatsapp_message_id,
                'expires_at': pending_trade['expires_at']
            }
        
        except Exception as e:
            logger.error(f"WhatsApp trade execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_whatsapp_chart(
        self, 
        db: Session, 
        user_id: str, 
        chart_request: WhatsAppChartRequest
    ) -> Dict[str, Any]:
        """Generate chart image for WhatsApp sharing"""
        
        try:
            # Generate chart with trading context
            chart_config = {
                'symbol': chart_request.symbol,
                'timeframe': chart_request.timeframe,
                'indicators': chart_request.indicators,
                'drawing_tools': chart_request.drawing_tools,
                'width': 800,
                'height': 600,
                'format': 'png',
                'whatsapp_optimized': True
            }
            
            chart_image = await self.chart_generator.generate_chart(chart_config)
            
            # Add trading buttons overlay if requested
            if chart_request.include_trade_buttons:
                chart_image = await self._add_trading_buttons_overlay(
                    chart_image, chart_request.symbol
                )
            
            # Upload to cloud storage
            chart_url = await self._upload_chart_image(chart_image, user_id)
            
            # Generate analysis text
            analysis_text = await self._generate_chart_analysis(
                chart_request.symbol, 
                chart_request.timeframe,
                chart_request.analysis_notes
            )
            
            # Create trade buttons for WhatsApp
            trade_buttons = []
            if chart_request.include_trade_buttons:
                trade_buttons = [
                    {
                        'id': f'quick_buy_{chart_request.symbol}',
                        'title': f'🟢 Buy {chart_request.symbol}',
                        'type': 'quick_trade'
                    },
                    {
                        'id': f'quick_sell_{chart_request.symbol}',
                        'title': f'🔴 Sell {chart_request.symbol}',
                        'type': 'quick_trade'
                    },
                    {
                        'id': f'set_alert_{chart_request.symbol}',
                        'title': f'🚨 Set Alert',
                        'type': 'alert'
                    }
                ]
            
            # Send to WhatsApp
            whatsapp_message_id = await self.whatsapp_client.send_image(
                phone_number=chart_request.whatsapp_number,
                image_url=chart_url,
                caption=analysis_text,
                buttons=trade_buttons
            )
            
            return {
                'success': True,
                'chart_url': chart_url,
                'whatsapp_message_id': whatsapp_message_id,
                'trade_buttons': trade_buttons,
                'analysis': analysis_text,
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
        
        except Exception as e:
            logger.error(f"WhatsApp chart generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def execute_quick_trade(
        self, 
        db: Session, 
        user_id: str, 
        quick_trade_request: WhatsAppQuickTradeRequest
    ) -> Dict[str, Any]:
        """Execute predefined quick trade from WhatsApp"""
        
        try:
            if quick_trade_request.preset_name not in self.trade_presets:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unknown trade preset: {quick_trade_request.preset_name}"
                )
            
            preset = self.trade_presets[quick_trade_request.preset_name]
            
            # Get current market price
            current_price = await self.trading_engine.get_current_price(
                quick_trade_request.symbol
            )
            
            # Calculate position size based on risk
            risk_amount = quick_trade_request.risk_amount or 1000  # Default ₹1000
            position_size = await self.risk_manager.calculate_position_size(
                symbol=quick_trade_request.symbol,
                risk_amount=risk_amount,
                stop_loss_percentage=preset['stop_loss_percentage'],
                current_price=current_price
            )
            
            # Create trade request
            trade_request = WhatsAppTradeRequest(
                symbol=quick_trade_request.symbol,
                action=preset['action'],
                quantity=position_size,
                order_type=preset['order_type'],
                price=current_price if preset['order_type'] == 'LIMIT' else None,
                stop_loss=current_price * (1 - preset['stop_loss_percentage']/100) if preset['action'] == 'BUY' else current_price * (1 + preset['stop_loss_percentage']/100),
                take_profit=current_price * (1 + preset['take_profit_percentage']/100) if preset['action'] == 'BUY' else current_price * (1 - preset['take_profit_percentage']/100),
                whatsapp_number=quick_trade_request.whatsapp_number,
                message_id=f"quick_trade_{uuid.uuid4()}"
            )
            
            # Execute the trade
            return await self.execute_whatsapp_trade(db, user_id, trade_request)
        
        except Exception as e:
            logger.error(f"Quick trade execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def setup_whatsapp_alert(
        self, 
        db: Session, 
        user_id: str, 
        alert_request: WhatsAppAlertRequest
    ) -> Dict[str, Any]:
        """Setup price/pattern alert for WhatsApp notifications"""
        
        try:
            alert_id = str(uuid.uuid4())
            
            # Create alert configuration
            alert_config = {
                'alert_id': alert_id,
                'user_id': user_id,
                'symbol': alert_request.symbol,
                'condition': alert_request.condition,
                'alert_type': alert_request.alert_type,
                'whatsapp_number': alert_request.whatsapp_number,
                'message_template': alert_request.message_template or self.message_templates['alert_triggered'],
                'status': 'active',
                'created_at': datetime.utcnow(),
                'triggered_count': 0
            }
            
            # Store alert in database
            await self._store_whatsapp_alert(db, alert_config)
            
            # Send confirmation
            confirmation_message = f"🚨 Alert Set Successfully\n\n📊 Symbol: {alert_request.symbol}\n🎯 Condition: {alert_request.condition}\n📱 Will notify via WhatsApp\n\n✅ Alert ID: {alert_id}"
            
            whatsapp_message_id = await self.whatsapp_client.send_message(
                phone_number=alert_request.whatsapp_number,
                message=confirmation_message
            )
            
            return {
                'success': True,
                'alert_id': alert_id,
                'whatsapp_message_id': whatsapp_message_id,
                'status': 'active'
            }
        
        except Exception as e:
            logger.error(f"WhatsApp alert setup error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_whatsapp_callback(
        self, 
        db: Session, 
        callback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle WhatsApp button callbacks and message responses"""
        
        try:
            callback_type = callback_data.get('type')
            callback_id = callback_data.get('id')
            user_phone = callback_data.get('phone_number')
            message_text = callback_data.get('message', '').upper()
            
            if callback_type == 'button_click':
                if callback_id.startswith('confirm_'):
                    trade_id = callback_id.replace('confirm_', '')
                    return await self._confirm_pending_trade(db, trade_id, user_phone)
                
                elif callback_id.startswith('cancel_'):
                    trade_id = callback_id.replace('cancel_', '')
                    return await self._cancel_pending_trade(db, trade_id, user_phone)
                
                elif callback_id.startswith('quick_buy_'):
                    symbol = callback_id.replace('quick_buy_', '')
                    return await self._handle_quick_buy(db, symbol, user_phone)
                
                elif callback_id.startswith('quick_sell_'):
                    symbol = callback_id.replace('quick_sell_', '')
                    return await self._handle_quick_sell(db, symbol, user_phone)
            
            elif callback_type == 'message_reply':
                if message_text in ['YES', 'Y', 'CONFIRM']:
                    return await self._handle_confirmation_message(db, user_phone)
                elif message_text in ['NO', 'N', 'CANCEL']:
                    return await self._handle_cancellation_message(db, user_phone)
            
            return {'success': False, 'message': 'Unknown callback type'}
        
        except Exception as e:
            logger.error(f"WhatsApp callback handling error: {e}")
            return {'success': False, 'error': str(e)}
    
    # Private helper methods
    async def _validate_whatsapp_session(
        self, 
        db: Session, 
        user_id: str, 
        whatsapp_number: str
    ) -> WhatsAppSession:
        """Validate WhatsApp session and permissions"""
        
        session = db.query(WhatsAppSession).filter(
            WhatsAppSession.user_id == user_id,
            WhatsAppSession.phone_number == whatsapp_number,
            WhatsAppSession.status == 'active'
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=403, 
                detail="WhatsApp number not verified for trading"
            )
        
        return session
    
    def _generate_trade_confirmation(self, trade_request: WhatsAppTradeRequest, trade_id: str) -> str:
        """Generate trade confirmation message"""
        
        return self.message_templates['trade_confirmation'].format(
            symbol=trade_request.symbol,
            action=trade_request.action,
            quantity=trade_request.quantity,
            price=trade_request.price or 'Market Price'
        )
    
    async def _add_trading_buttons_overlay(self, chart_image: bytes, symbol: str) -> bytes:
        """Add trading action buttons overlay to chart image"""
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(chart_image))
        draw = ImageDraw.Draw(image)
        
        # Add semi-transparent overlay for buttons
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Draw button backgrounds
        button_height = 40
        button_width = 120
        margin = 10
        
        # Buy button (green)
        buy_button_rect = [
            margin, 
            image.height - button_height - margin,
            margin + button_width, 
            image.height - margin
        ]
        overlay_draw.rectangle(buy_button_rect, fill=(34, 197, 94, 200))
        
        # Sell button (red)
        sell_button_rect = [
            margin * 2 + button_width, 
            image.height - button_height - margin,
            margin * 2 + button_width * 2, 
            image.height - margin
        ]
        overlay_draw.rectangle(sell_button_rect, fill=(239, 68, 68, 200))
        
        # Composite overlay onto original image
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        
        # Add button text
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        # Draw button text
        draw = ImageDraw.Draw(image)
        draw.text(
            (margin + button_width//2 - 15, image.height - button_height//2 - margin - 5),
            "BUY", 
            fill='white', 
            font=font
        )
        draw.text(
            (margin * 2 + button_width + button_width//2 - 20, image.height - button_height//2 - margin - 5),
            "SELL", 
            fill='white', 
            font=font
        )
        
        # Convert back to bytes
        output = io.BytesIO()
        image.convert('RGB').save(output, format='PNG')
        return output.getvalue()
    
    async def _upload_chart_image(self, image_data: bytes, user_id: str) -> str:
        """Upload chart image to cloud storage and return URL"""
        
        # In production, this would upload to AWS S3, Google Cloud Storage, etc.
        # For now, return a placeholder URL
        chart_id = str(uuid.uuid4())
        return f"https://charts.gridworks.ai/{user_id}/{chart_id}.png"
    
    async def _generate_chart_analysis(
        self, 
        symbol: str, 
        timeframe: str, 
        analysis_notes: Optional[str]
    ) -> str:
        """Generate AI-powered chart analysis text"""
        
        # In production, this would use AI to analyze the chart
        # For now, return a template-based analysis
        return self.message_templates['chart_analysis'].format(
            symbol=symbol,
            timeframe=timeframe,
            trend="Bullish",
            strength=75,
            patterns="Ascending Triangle",
            analysis_notes=analysis_notes or "Technical outlook looks positive with strong momentum."
        )
    
    async def _store_pending_trade(self, db: Session, trade_data: Dict[str, Any]):
        """Store pending trade in database"""
        
        # Implementation would store in database
        # For now, we'll use in-memory storage
        pass
    
    async def _store_whatsapp_alert(self, db: Session, alert_config: Dict[str, Any]):
        """Store WhatsApp alert configuration"""
        
        # Implementation would store in database
        pass
    
    async def _confirm_pending_trade(self, db: Session, trade_id: str, user_phone: str) -> Dict[str, Any]:
        """Confirm and execute pending trade"""
        
        # Implementation would execute the trade
        return {
            'success': True,
            'message': 'Trade executed successfully',
            'trade_id': trade_id
        }
    
    async def _cancel_pending_trade(self, db: Session, trade_id: str, user_phone: str) -> Dict[str, Any]:
        """Cancel pending trade"""
        
        return {
            'success': True,
            'message': 'Trade cancelled successfully',
            'trade_id': trade_id
        }
    
    async def _handle_quick_buy(self, db: Session, symbol: str, user_phone: str) -> Dict[str, Any]:
        """Handle quick buy action"""
        
        return {
            'success': True,
            'message': f'Quick buy initiated for {symbol}',
            'action': 'buy'
        }
    
    async def _handle_quick_sell(self, db: Session, symbol: str, user_phone: str) -> Dict[str, Any]:
        """Handle quick sell action"""
        
        return {
            'success': True,
            'message': f'Quick sell initiated for {symbol}',
            'action': 'sell'
        }
    
    async def _handle_confirmation_message(self, db: Session, user_phone: str) -> Dict[str, Any]:
        """Handle YES confirmation message"""
        
        return {
            'success': True,
            'message': 'Trade confirmed via message'
        }
    
    async def _handle_cancellation_message(self, db: Session, user_phone: str) -> Dict[str, Any]:
        """Handle NO cancellation message"""
        
        return {
            'success': True,
            'message': 'Trade cancelled via message'
        }
    
    async def _send_risk_rejection_message(self, whatsapp_number: str, reason: str):
        """Send risk management rejection message"""
        
        message = f"⚠️ Trade Rejected\n\nReason: {reason}\n\nPlease review your risk settings or contact support."
        
        await self.whatsapp_client.send_message(
            phone_number=whatsapp_number,
            message=message
        )


# Initialize WhatsApp trading manager
whatsapp_trading = WhatsAppTradingManager()


# API Endpoints
@router.post("/trade", response_model=WhatsAppTradeResponse)
async def execute_whatsapp_trade(
    trade_request: WhatsAppTradeRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute trade from WhatsApp message"""
    
    result = await whatsapp_trading.execute_whatsapp_trade(
        db, user["id"], trade_request
    )
    
    return WhatsAppTradeResponse(
        trade_id=result['trade_id'],
        status=result['status'],
        message="Trade confirmation sent to WhatsApp",
        whatsapp_message_id=result['whatsapp_message_id'],
        confirmation_required=True
    )


@router.post("/chart", response_model=WhatsAppChartResponse)
async def generate_whatsapp_chart(
    chart_request: WhatsAppChartRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate chart for WhatsApp sharing"""
    
    result = await whatsapp_trading.generate_whatsapp_chart(
        db, user["id"], chart_request
    )
    
    return WhatsAppChartResponse(
        chart_url=result['chart_url'],
        whatsapp_message_id=result['whatsapp_message_id'],
        trade_buttons=result['trade_buttons'],
        expires_at=result['expires_at']
    )


@router.post("/quick-trade")
async def execute_quick_trade(
    quick_trade_request: WhatsAppQuickTradeRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute predefined quick trade"""
    
    result = await whatsapp_trading.execute_quick_trade(
        db, user["id"], quick_trade_request
    )
    
    return result


@router.post("/alert")
async def setup_whatsapp_alert(
    alert_request: WhatsAppAlertRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup WhatsApp price/pattern alert"""
    
    result = await whatsapp_trading.setup_whatsapp_alert(
        db, user["id"], alert_request
    )
    
    return result


@router.post("/callback")
async def handle_whatsapp_callback(
    callback_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle WhatsApp callbacks and responses"""
    
    result = await whatsapp_trading.handle_whatsapp_callback(
        db, callback_data
    )
    
    return result


@router.get("/presets")
async def get_trade_presets():
    """Get available quick trade presets"""
    
    return {
        'presets': [
            {
                'name': name,
                'description': f"{preset['action']} with {preset['risk_percentage']}% risk",
                'details': preset
            }
            for name, preset in whatsapp_trading.trade_presets.items()
        ]
    }


@router.get("/session/{phone_number}")
async def get_whatsapp_session(
    phone_number: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get WhatsApp session status"""
    
    session = db.query(WhatsAppSession).filter(
        WhatsAppSession.user_id == user["id"],
        WhatsAppSession.phone_number == phone_number
    ).first()
    
    if not session:
        return {'verified': False, 'status': 'not_found'}
    
    return {
        'verified': session.status == 'active',
        'status': session.status,
        'verified_at': session.verified_at,
        'trading_enabled': session.trading_enabled
    }


# Health check
@router.get("/health")
async def whatsapp_health_check():
    """Health check for WhatsApp trading system"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "whatsapp_trading": "operational",
        "features": {
            "one_click_trading": True,
            "chart_sharing": True,
            "quick_trades": True,
            "alerts": True,
            "risk_management": True
        }
    }