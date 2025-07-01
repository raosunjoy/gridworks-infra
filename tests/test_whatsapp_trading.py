"""
Comprehensive test suite for WhatsApp Trading Integration
Tests all functionality including trade execution, chart sharing, and callbacks
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
import json
import uuid

from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.integrations.whatsapp_trading import (
    WhatsAppTradingManager, 
    WhatsAppTradeRequest,
    WhatsAppChartRequest,
    WhatsAppQuickTradeRequest,
    WhatsAppAlertRequest
)


class TestWhatsAppTradingManagerInit:
    """Test WhatsApp Trading Manager initialization"""
    
    def test_whatsapp_manager_initialization(self):
        """Test manager initialization with default settings"""
        manager = WhatsAppTradingManager()
        
        assert manager.whatsapp_client is not None
        assert manager.trading_engine is not None
        assert manager.chart_generator is not None
        assert manager.risk_manager is not None
        
        # Check trade presets
        assert 'scalp_buy' in manager.trade_presets
        assert 'scalp_sell' in manager.trade_presets
        assert 'swing_buy' in manager.trade_presets
        assert 'swing_sell' in manager.trade_presets
        assert 'momentum_buy' in manager.trade_presets
        
        # Check message templates
        assert 'trade_confirmation' in manager.message_templates
        assert 'trade_executed' in manager.message_templates
        assert 'chart_analysis' in manager.message_templates
        assert 'alert_triggered' in manager.message_templates
    
    def test_trade_presets_structure(self):
        """Test trade presets have correct structure"""
        manager = WhatsAppTradingManager()
        
        for preset_name, preset in manager.trade_presets.items():
            assert 'action' in preset
            assert preset['action'] in ['BUY', 'SELL']
            assert 'order_type' in preset
            assert 'risk_percentage' in preset
            assert 'stop_loss_percentage' in preset
            assert 'take_profit_percentage' in preset
            assert isinstance(preset['risk_percentage'], (int, float))
            assert isinstance(preset['stop_loss_percentage'], (int, float))
            assert isinstance(preset['take_profit_percentage'], (int, float))


class TestWhatsAppTradeExecution:
    """Test WhatsApp trade execution functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_trade_execution(
        self, 
        db_session, 
        test_user, 
        mock_whatsapp_client,
        mock_risk_manager
    ):
        """Test successful trade execution flow"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        manager.risk_manager = mock_risk_manager
        
        # Mock WhatsApp session validation
        with patch.object(manager, '_validate_whatsapp_session', 
                         return_value=Mock(user_id=test_user.id)):
            
            trade_request = WhatsAppTradeRequest(
                symbol="RELIANCE",
                action="BUY",
                quantity=10,
                order_type="MARKET",
                price=2500.0,
                whatsapp_number="+919876543210",
                message_id="msg_123"
            )
            
            result = await manager.execute_whatsapp_trade(
                db_session, test_user.id, trade_request
            )
            
            assert result['success'] is True
            assert 'trade_id' in result
            assert result['status'] == 'pending_confirmation'
            assert 'whatsapp_message_id' in result
            assert 'expires_at' in result
            
            # Verify WhatsApp message was sent
            mock_whatsapp_client.send_message.assert_called_once()
            call_args = mock_whatsapp_client.send_message.call_args
            assert call_args[1]['phone_number'] == "+919876543210"
            assert 'buttons' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_trade_execution_risk_rejection(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client,
        mock_risk_manager
    ):
        """Test trade execution with risk management rejection"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        manager.risk_manager = mock_risk_manager
        
        # Configure risk manager to reject trade
        mock_risk_manager.validate_trade.return_value = {
            'approved': False,
            'reason': 'Exceeds daily risk limit'
        }
        
        with patch.object(manager, '_validate_whatsapp_session', 
                         return_value=Mock(user_id=test_user.id)):
            
            trade_request = WhatsAppTradeRequest(
                symbol="RELIANCE",
                action="BUY",
                quantity=1000,  # Large quantity to trigger risk rejection
                whatsapp_number="+919876543210",
                message_id="msg_123"
            )
            
            result = await manager.execute_whatsapp_trade(
                db_session, test_user.id, trade_request
            )
            
            assert result['success'] is False
            assert result['reason'] == 'Exceeds daily risk limit'
            assert 'risk_check' in result
            
            # Should not send confirmation message
            mock_whatsapp_client.send_message.assert_called_once()
            # But should send rejection message
            call_args = mock_whatsapp_client.send_message.call_args
            assert "Trade Rejected" in call_args[1]['message']
    
    @pytest.mark.asyncio
    async def test_trade_execution_invalid_whatsapp_session(
        self, 
        db_session, 
        test_user
    ):
        """Test trade execution with invalid WhatsApp session"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_validate_whatsapp_session', 
                         side_effect=HTTPException(status_code=403, detail="Not verified")):
            
            trade_request = WhatsAppTradeRequest(
                symbol="RELIANCE",
                action="BUY",
                quantity=10,
                whatsapp_number="+919876543210",
                message_id="msg_123"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.execute_whatsapp_trade(
                    db_session, test_user.id, trade_request
                )
            
            assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_trade_confirmation_message_generation(self):
        """Test trade confirmation message generation"""
        manager = WhatsAppTradingManager()
        
        trade_request = WhatsAppTradeRequest(
            symbol="NIFTY",
            action="SELL",
            quantity=25,
            price=18500.0,
            whatsapp_number="+919876543210",
            message_id="msg_123"
        )
        
        message = manager._generate_trade_confirmation(trade_request, "trade_123")
        
        assert "NIFTY" in message
        assert "SELL" in message
        assert "25" in message
        assert "18500" in message
        assert "YES" in message
        assert "NO" in message
        assert "5 minutes" in message


class TestWhatsAppQuickTrades:
    """Test WhatsApp quick trade functionality"""
    
    @pytest.mark.asyncio
    async def test_scalp_buy_quick_trade(
        self, 
        db_session, 
        test_user,
        mock_trading_engine,
        mock_risk_manager
    ):
        """Test scalp buy quick trade execution"""
        manager = WhatsAppTradingManager()
        manager.trading_engine = mock_trading_engine
        manager.risk_manager = mock_risk_manager
        
        # Mock current price
        mock_trading_engine.get_current_price.return_value = 2500.0
        mock_risk_manager.calculate_position_size.return_value = 5
        
        with patch.object(manager, 'execute_whatsapp_trade', 
                         return_value={'success': True, 'trade_id': 'quick_123'}) as mock_execute:
            
            quick_trade_request = WhatsAppQuickTradeRequest(
                preset_name="scalp_buy",
                symbol="RELIANCE",
                whatsapp_number="+919876543210",
                risk_amount=1000.0
            )
            
            result = await manager.execute_quick_trade(
                db_session, test_user.id, quick_trade_request
            )
            
            assert result['success'] is True
            assert result['trade_id'] == 'quick_123'
            
            # Verify execute_whatsapp_trade was called with correct parameters
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0][2]  # trade_request argument
            
            assert call_args.symbol == "RELIANCE"
            assert call_args.action == "BUY"
            assert call_args.quantity == 5
            assert call_args.order_type == "MARKET"
            assert call_args.whatsapp_number == "+919876543210"
    
    @pytest.mark.asyncio
    async def test_swing_sell_quick_trade(
        self, 
        db_session, 
        test_user,
        mock_trading_engine,
        mock_risk_manager
    ):
        """Test swing sell quick trade execution"""
        manager = WhatsAppTradingManager()
        manager.trading_engine = mock_trading_engine
        manager.risk_manager = mock_risk_manager
        
        mock_trading_engine.get_current_price.return_value = 18500.0
        mock_risk_manager.calculate_position_size.return_value = 15
        
        with patch.object(manager, 'execute_whatsapp_trade', 
                         return_value={'success': True, 'trade_id': 'swing_456'}) as mock_execute:
            
            quick_trade_request = WhatsAppQuickTradeRequest(
                preset_name="swing_sell",
                symbol="NIFTY",
                whatsapp_number="+919876543210"
            )
            
            result = await manager.execute_quick_trade(
                db_session, test_user.id, quick_trade_request
            )
            
            # Verify swing trade parameters
            call_args = mock_execute.call_args[0][2]
            
            assert call_args.action == "SELL"
            assert call_args.order_type == "LIMIT"
            assert call_args.price == 18500.0  # LIMIT order should have price
            
            # Check stop loss and take profit calculations
            assert call_args.stop_loss == 18500.0 * 1.01  # 1% above for SELL
            assert call_args.take_profit == 18500.0 * 0.97  # 3% below for SELL
    
    @pytest.mark.asyncio
    async def test_invalid_preset_quick_trade(self, db_session, test_user):
        """Test quick trade with invalid preset name"""
        manager = WhatsAppTradingManager()
        
        quick_trade_request = WhatsAppQuickTradeRequest(
            preset_name="invalid_preset",
            symbol="RELIANCE",
            whatsapp_number="+919876543210"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await manager.execute_quick_trade(
                db_session, test_user.id, quick_trade_request
            )
        
        assert exc_info.value.status_code == 400
        assert "Unknown trade preset" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_momentum_buy_with_custom_risk(
        self, 
        db_session, 
        test_user,
        mock_trading_engine,
        mock_risk_manager
    ):
        """Test momentum buy with custom risk amount"""
        manager = WhatsAppTradingManager()
        manager.trading_engine = mock_trading_engine
        manager.risk_manager = mock_risk_manager
        
        mock_trading_engine.get_current_price.return_value = 1500.0
        mock_risk_manager.calculate_position_size.return_value = 20
        
        with patch.object(manager, 'execute_whatsapp_trade', 
                         return_value={'success': True}) as mock_execute:
            
            quick_trade_request = WhatsAppQuickTradeRequest(
                preset_name="momentum_buy",
                symbol="ITC",
                whatsapp_number="+919876543210",
                risk_amount=2500.0  # Custom risk amount
            )
            
            await manager.execute_quick_trade(
                db_session, test_user.id, quick_trade_request
            )
            
            # Verify risk manager was called with custom amount
            mock_risk_manager.calculate_position_size.assert_called_once_with(
                symbol="ITC",
                risk_amount=2500.0,
                stop_loss_percentage=0.5,  # momentum_buy stop loss
                current_price=1500.0
            )


class TestWhatsAppChartSharing:
    """Test WhatsApp chart sharing functionality"""
    
    @pytest.mark.asyncio
    async def test_chart_generation_with_buttons(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test chart generation with trading buttons"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager.chart_generator, 'generate_chart',
                         return_value=b'fake_chart_image') as mock_chart:
            with patch.object(manager, '_add_trading_buttons_overlay',
                             return_value=b'chart_with_buttons') as mock_overlay:
                with patch.object(manager, '_upload_chart_image',
                                 return_value='https://charts.example.com/chart123.png') as mock_upload:
                    with patch.object(manager, '_generate_chart_analysis',
                                     return_value='Strong bullish momentum detected') as mock_analysis:
                        
                        chart_request = WhatsAppChartRequest(
                            symbol="RELIANCE",
                            timeframe="15m",
                            indicators=["RSI", "MACD"],
                            whatsapp_number="+919876543210",
                            include_trade_buttons=True,
                            analysis_notes="Custom analysis notes"
                        )
                        
                        result = await manager.generate_whatsapp_chart(
                            db_session, test_user.id, chart_request
                        )
                        
                        assert result['success'] is True
                        assert result['chart_url'] == 'https://charts.example.com/chart123.png'
                        assert 'whatsapp_message_id' in result
                        assert len(result['trade_buttons']) == 3  # Buy, Sell, Alert
                        assert result['analysis'] == 'Strong bullish momentum detected'
                        
                        # Verify chart generation was called with correct config
                        mock_chart.assert_called_once()
                        chart_config = mock_chart.call_args[0][0]
                        assert chart_config['symbol'] == "RELIANCE"
                        assert chart_config['timeframe'] == "15m"
                        assert chart_config['indicators'] == ["RSI", "MACD"]
                        assert chart_config['whatsapp_optimized'] is True
                        
                        # Verify buttons overlay was applied
                        mock_overlay.assert_called_once_with(b'fake_chart_image', "RELIANCE")
                        
                        # Verify WhatsApp message was sent
                        mock_whatsapp_client.send_image.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chart_generation_without_buttons(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test chart generation without trading buttons"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager.chart_generator, 'generate_chart',
                         return_value=b'fake_chart_image'):
            with patch.object(manager, '_upload_chart_image',
                             return_value='https://charts.example.com/chart123.png'):
                with patch.object(manager, '_generate_chart_analysis',
                                 return_value='Technical analysis'):
                    
                    chart_request = WhatsAppChartRequest(
                        symbol="NIFTY",
                        timeframe="5m",
                        whatsapp_number="+919876543210",
                        include_trade_buttons=False
                    )
                    
                    result = await manager.generate_whatsapp_chart(
                        db_session, test_user.id, chart_request
                    )
                    
                    assert result['success'] is True
                    assert len(result['trade_buttons']) == 0  # No buttons
    
    @pytest.mark.asyncio
    async def test_trading_buttons_overlay_generation(self):
        """Test trading buttons overlay generation"""
        manager = WhatsAppTradingManager()
        
        # Mock PIL operations
        with patch('app.integrations.whatsapp_trading.Image') as mock_image:
            with patch('app.integrations.whatsapp_trading.ImageDraw') as mock_draw:
                with patch('app.integrations.whatsapp_trading.ImageFont') as mock_font:
                    
                    # Setup mocks
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    mock_img.height = 600
                    mock_image.open.return_value = mock_img
                    mock_image.new.return_value = Mock()
                    mock_image.alpha_composite.return_value = mock_img
                    
                    mock_draw_obj = Mock()
                    mock_draw.Draw.return_value = mock_draw_obj
                    
                    mock_font.truetype.return_value = Mock()
                    
                    # Mock BytesIO
                    with patch('app.integrations.whatsapp_trading.io.BytesIO') as mock_bytesio:
                        mock_output = Mock()
                        mock_output.getvalue.return_value = b'image_with_buttons'
                        mock_bytesio.return_value = mock_output
                        
                        result = await manager._add_trading_buttons_overlay(
                            b'original_image', 'RELIANCE'
                        )
                        
                        assert result == b'image_with_buttons'
                        
                        # Verify drawing operations
                        assert mock_draw_obj.rectangle.call_count == 2  # Buy and Sell buttons
                        assert mock_draw_obj.text.call_count == 2  # Button text
    
    @pytest.mark.asyncio
    async def test_chart_analysis_generation(self):
        """Test AI chart analysis generation"""
        manager = WhatsAppTradingManager()
        
        analysis = await manager._generate_chart_analysis(
            symbol="RELIANCE",
            timeframe="15m",
            analysis_notes="Custom insights here"
        )
        
        assert "RELIANCE" in analysis
        assert "15m" in analysis
        assert "Custom insights here" in analysis
        assert "Bullish" in analysis or "Bearish" in analysis  # Should have trend
        assert "%" in analysis  # Should have percentage strength


class TestWhatsAppAlerts:
    """Test WhatsApp alert functionality"""
    
    @pytest.mark.asyncio
    async def test_price_alert_setup(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test price alert setup"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager, '_store_whatsapp_alert') as mock_store:
            
            alert_request = WhatsAppAlertRequest(
                symbol="RELIANCE",
                condition={"type": "price_above", "value": 2600.0},
                alert_type="PRICE",
                whatsapp_number="+919876543210",
                message_template="Custom alert: {symbol} crossed {target_price}"
            )
            
            result = await manager.setup_whatsapp_alert(
                db_session, test_user.id, alert_request
            )
            
            assert result['success'] is True
            assert 'alert_id' in result
            assert 'whatsapp_message_id' in result
            assert result['status'] == 'active'
            
            # Verify alert was stored
            mock_store.assert_called_once()
            stored_alert = mock_store.call_args[0][1]
            assert stored_alert['symbol'] == "RELIANCE"
            assert stored_alert['alert_type'] == "PRICE"
            assert stored_alert['status'] == 'active'
            
            # Verify confirmation message
            mock_whatsapp_client.send_message.assert_called_once()
            message = mock_whatsapp_client.send_message.call_args[1]['message']
            assert "Alert Set Successfully" in message
            assert "RELIANCE" in message
    
    @pytest.mark.asyncio
    async def test_pattern_alert_setup(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test pattern alert setup"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager, '_store_whatsapp_alert') as mock_store:
            
            alert_request = WhatsAppAlertRequest(
                symbol="NIFTY",
                condition={"pattern": "head_and_shoulders", "confidence": 0.8},
                alert_type="PATTERN",
                whatsapp_number="+919876543210"
            )
            
            result = await manager.setup_whatsapp_alert(
                db_session, test_user.id, alert_request
            )
            
            assert result['success'] is True
            
            # Verify pattern alert configuration
            stored_alert = mock_store.call_args[0][1]
            assert stored_alert['alert_type'] == "PATTERN"
            assert "pattern" in stored_alert['condition']
    
    @pytest.mark.asyncio
    async def test_indicator_alert_setup(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test indicator alert setup"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager, '_store_whatsapp_alert') as mock_store:
            
            alert_request = WhatsAppAlertRequest(
                symbol="RELIANCE",
                condition={"indicator": "RSI", "condition": "oversold", "value": 30},
                alert_type="INDICATOR",
                whatsapp_number="+919876543210"
            )
            
            result = await manager.setup_whatsapp_alert(
                db_session, test_user.id, alert_request
            )
            
            assert result['success'] is True
            
            # Verify indicator alert configuration
            stored_alert = mock_store.call_args[0][1]
            assert stored_alert['alert_type'] == "INDICATOR"
            assert "indicator" in stored_alert['condition']


class TestWhatsAppCallbacks:
    """Test WhatsApp callback handling"""
    
    @pytest.mark.asyncio
    async def test_trade_confirmation_callback(self, db_session):
        """Test trade confirmation button callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_confirm_pending_trade',
                         return_value={'success': True, 'trade_id': 'trade_123'}) as mock_confirm:
            
            callback_data = {
                'type': 'button_click',
                'id': 'confirm_trade_123',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            assert result['trade_id'] == 'trade_123'
            
            mock_confirm.assert_called_once_with(db_session, 'trade_123', '+919876543210')
    
    @pytest.mark.asyncio
    async def test_trade_cancellation_callback(self, db_session):
        """Test trade cancellation button callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_cancel_pending_trade',
                         return_value={'success': True, 'trade_id': 'trade_123'}) as mock_cancel:
            
            callback_data = {
                'type': 'button_click',
                'id': 'cancel_trade_123',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            
            mock_cancel.assert_called_once_with(db_session, 'trade_123', '+919876543210')
    
    @pytest.mark.asyncio
    async def test_quick_buy_callback(self, db_session):
        """Test quick buy button callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_handle_quick_buy',
                         return_value={'success': True, 'action': 'buy'}) as mock_quick_buy:
            
            callback_data = {
                'type': 'button_click',
                'id': 'quick_buy_RELIANCE',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            assert result['action'] == 'buy'
            
            mock_quick_buy.assert_called_once_with(db_session, 'RELIANCE', '+919876543210')
    
    @pytest.mark.asyncio
    async def test_quick_sell_callback(self, db_session):
        """Test quick sell button callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_handle_quick_sell',
                         return_value={'success': True, 'action': 'sell'}) as mock_quick_sell:
            
            callback_data = {
                'type': 'button_click',
                'id': 'quick_sell_NIFTY',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            assert result['action'] == 'sell'
            
            mock_quick_sell.assert_called_once_with(db_session, 'NIFTY', '+919876543210')
    
    @pytest.mark.asyncio
    async def test_text_confirmation_callback(self, db_session):
        """Test text message confirmation callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_handle_confirmation_message',
                         return_value={'success': True}) as mock_confirm:
            
            callback_data = {
                'type': 'message_reply',
                'message': 'YES',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            
            mock_confirm.assert_called_once_with(db_session, '+919876543210')
    
    @pytest.mark.asyncio
    async def test_text_cancellation_callback(self, db_session):
        """Test text message cancellation callback"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_handle_cancellation_message',
                         return_value={'success': True}) as mock_cancel:
            
            callback_data = {
                'type': 'message_reply',
                'message': 'NO',
                'phone_number': '+919876543210'
            }
            
            result = await manager.handle_whatsapp_callback(db_session, callback_data)
            
            assert result['success'] is True
            
            mock_cancel.assert_called_once_with(db_session, '+919876543210')
    
    @pytest.mark.asyncio
    async def test_unknown_callback_type(self, db_session):
        """Test handling of unknown callback type"""
        manager = WhatsAppTradingManager()
        
        callback_data = {
            'type': 'unknown_type',
            'id': 'unknown_123',
            'phone_number': '+919876543210'
        }
        
        result = await manager.handle_whatsapp_callback(db_session, callback_data)
        
        assert result['success'] is False
        assert 'Unknown callback type' in result['message']


class TestWhatsAppValidation:
    """Test WhatsApp validation and security"""
    
    @pytest.mark.asyncio
    async def test_whatsapp_session_validation_success(self, db_session, test_user):
        """Test successful WhatsApp session validation"""
        manager = WhatsAppTradingManager()
        
        # Mock valid session
        mock_session = Mock()
        mock_session.user_id = test_user.id
        mock_session.phone_number = "+919876543210"
        mock_session.status = 'active'
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_session
            
            result = await manager._validate_whatsapp_session(
                db_session, test_user.id, "+919876543210"
            )
            
            assert result == mock_session
    
    @pytest.mark.asyncio
    async def test_whatsapp_session_validation_failure(self, db_session, test_user):
        """Test WhatsApp session validation failure"""
        manager = WhatsAppTradingManager()
        
        # Mock no session found
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await manager._validate_whatsapp_session(
                    db_session, test_user.id, "+919876543210"
                )
            
            assert exc_info.value.status_code == 403
            assert "not verified" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_risk_rejection_message_sending(self, mock_whatsapp_client):
        """Test risk rejection message sending"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        await manager._send_risk_rejection_message(
            "+919876543210", "Position size exceeds risk limit"
        )
        
        mock_whatsapp_client.send_message.assert_called_once()
        call_args = mock_whatsapp_client.send_message.call_args
        
        assert call_args[1]['phone_number'] == "+919876543210"
        message = call_args[1]['message']
        assert "Trade Rejected" in message
        assert "Position size exceeds risk limit" in message


class TestWhatsAppAPIEndpoints:
    """Test WhatsApp trading API endpoints"""
    
    def test_execute_trade_endpoint(self, test_client, auth_headers):
        """Test /api/v1/whatsapp/trade endpoint"""
        trade_data = {
            "symbol": "RELIANCE",
            "action": "BUY",
            "quantity": 10,
            "whatsapp_number": "+919876543210",
            "message_id": "msg_123"
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_manager:
            mock_manager.execute_whatsapp_trade.return_value = {
                'trade_id': 'trade_123',
                'status': 'pending_confirmation',
                'whatsapp_message_id': 'wa_msg_456'
            }
            
            response = test_client.post(
                "/api/v1/whatsapp/trade",
                json=trade_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['trade_id'] == 'trade_123'
            assert data['status'] == 'pending_confirmation'
            assert data['confirmation_required'] is True
    
    def test_generate_chart_endpoint(self, test_client, auth_headers):
        """Test /api/v1/whatsapp/chart endpoint"""
        chart_data = {
            "symbol": "NIFTY",
            "timeframe": "15m",
            "indicators": ["RSI", "MACD"],
            "whatsapp_number": "+919876543210",
            "include_trade_buttons": True
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_manager:
            mock_manager.generate_whatsapp_chart.return_value = {
                'chart_url': 'https://charts.example.com/chart.png',
                'whatsapp_message_id': 'wa_chart_123',
                'trade_buttons': [{'id': 'buy_nifty', 'title': 'Buy NIFTY'}],
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
            
            response = test_client.post(
                "/api/v1/whatsapp/chart",
                json=chart_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 'chart_url' in data
            assert 'trade_buttons' in data
    
    def test_quick_trade_endpoint(self, test_client, auth_headers):
        """Test /api/v1/whatsapp/quick-trade endpoint"""
        quick_trade_data = {
            "preset_name": "scalp_buy",
            "symbol": "RELIANCE",
            "whatsapp_number": "+919876543210",
            "risk_amount": 1000.0
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_manager:
            mock_manager.execute_quick_trade.return_value = {
                'success': True,
                'trade_id': 'quick_trade_123'
            }
            
            response = test_client.post(
                "/api/v1/whatsapp/quick-trade",
                json=quick_trade_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['trade_id'] == 'quick_trade_123'
    
    def test_setup_alert_endpoint(self, test_client, auth_headers):
        """Test /api/v1/whatsapp/alert endpoint"""
        alert_data = {
            "symbol": "RELIANCE",
            "condition": {"type": "price_above", "value": 2600.0},
            "alert_type": "PRICE",
            "whatsapp_number": "+919876543210"
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_manager:
            mock_manager.setup_whatsapp_alert.return_value = {
                'success': True,
                'alert_id': 'alert_123',
                'whatsapp_message_id': 'wa_alert_456'
            }
            
            response = test_client.post(
                "/api/v1/whatsapp/alert",
                json=alert_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['alert_id'] == 'alert_123'
    
    def test_callback_endpoint(self, test_client):
        """Test /api/v1/whatsapp/callback endpoint"""
        callback_data = {
            "type": "button_click",
            "id": "confirm_trade_123",
            "phone_number": "+919876543210"
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_manager:
            mock_manager.handle_whatsapp_callback.return_value = {
                'success': True,
                'trade_id': 'trade_123'
            }
            
            response = test_client.post(
                "/api/v1/whatsapp/callback",
                json=callback_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
    
    def test_presets_endpoint(self, test_client):
        """Test /api/v1/whatsapp/presets endpoint"""
        response = test_client.get("/api/v1/whatsapp/presets")
        
        assert response.status_code == 200
        data = response.json()
        assert 'presets' in data
        assert len(data['presets']) == 5  # All preset types
        
        # Check preset structure
        for preset in data['presets']:
            assert 'name' in preset
            assert 'description' in preset
            assert 'details' in preset
    
    def test_health_endpoint(self, test_client):
        """Test /api/v1/whatsapp/health endpoint"""
        response = test_client.get("/api/v1/whatsapp/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['whatsapp_trading'] == 'operational'
        assert 'features' in data
        assert data['features']['one_click_trading'] is True
        assert data['features']['chart_sharing'] is True


class TestWhatsAppErrorHandling:
    """Test WhatsApp error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_whatsapp_client_failure(self, db_session, test_user):
        """Test handling of WhatsApp client failures"""
        manager = WhatsAppTradingManager()
        
        # Mock WhatsApp client to raise exception
        manager.whatsapp_client = Mock()
        manager.whatsapp_client.send_message = AsyncMock(side_effect=Exception("WhatsApp API error"))
        
        with patch.object(manager, '_validate_whatsapp_session', return_value=Mock()):
            with patch.object(manager.risk_manager, 'validate_trade',
                             return_value={'approved': True}):
                
                trade_request = WhatsAppTradeRequest(
                    symbol="RELIANCE",
                    action="BUY",
                    quantity=10,
                    whatsapp_number="+919876543210",
                    message_id="msg_123"
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    await manager.execute_whatsapp_trade(
                        db_session, test_user.id, trade_request
                    )
                
                assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_chart_generation_failure(self, db_session, test_user):
        """Test handling of chart generation failures"""
        manager = WhatsAppTradingManager()
        
        # Mock chart generator to raise exception
        manager.chart_generator.generate_chart = AsyncMock(
            side_effect=Exception("Chart generation failed")
        )
        
        chart_request = WhatsAppChartRequest(
            symbol="RELIANCE",
            whatsapp_number="+919876543210"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await manager.generate_whatsapp_chart(
                db_session, test_user.id, chart_request
            )
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_invalid_phone_number_format(self, db_session, test_user):
        """Test handling of invalid phone number format"""
        manager = WhatsAppTradingManager()
        
        with patch.object(manager, '_validate_whatsapp_session',
                         side_effect=HTTPException(status_code=403, detail="Invalid phone format")):
            
            trade_request = WhatsAppTradeRequest(
                symbol="RELIANCE",
                action="BUY",
                quantity=10,
                whatsapp_number="invalid_phone",  # Invalid format
                message_id="msg_123"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.execute_whatsapp_trade(
                    db_session, test_user.id, trade_request
                )
            
            assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_callback_error_handling(self, db_session):
        """Test callback error handling"""
        manager = WhatsAppTradingManager()
        
        # Test with malformed callback data
        callback_data = {
            # Missing required fields
            'type': 'button_click'
            # No 'id' or 'phone_number'
        }
        
        result = await manager.handle_whatsapp_callback(db_session, callback_data)
        
        # Should handle gracefully
        assert result['success'] is False
        assert 'error' in result or 'message' in result


class TestWhatsAppIntegration:
    """Integration tests for WhatsApp trading"""
    
    @pytest.mark.asyncio
    async def test_complete_trade_workflow(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client,
        mock_risk_manager,
        mock_trading_engine
    ):
        """Test complete trade workflow from request to execution"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        manager.risk_manager = mock_risk_manager
        manager.trading_engine = mock_trading_engine
        
        # Mock successful execution
        mock_trading_engine.execute_trade.return_value = {
            'success': True,
            'trade_id': 'executed_trade_123',
            'status': 'FILLED'
        }
        
        with patch.object(manager, '_validate_whatsapp_session', return_value=Mock()):
            with patch.object(manager, '_store_pending_trade') as mock_store:
                with patch.object(manager, '_confirm_pending_trade') as mock_confirm:
                    
                    # Step 1: Execute trade request
                    trade_request = WhatsAppTradeRequest(
                        symbol="RELIANCE",
                        action="BUY",
                        quantity=10,
                        whatsapp_number="+919876543210",
                        message_id="msg_123"
                    )
                    
                    trade_result = await manager.execute_whatsapp_trade(
                        db_session, test_user.id, trade_request
                    )
                    
                    assert trade_result['success'] is True
                    trade_id = trade_result['trade_id']
                    
                    # Step 2: Simulate confirmation callback
                    mock_confirm.return_value = {
                        'success': True,
                        'message': 'Trade executed successfully',
                        'trade_id': trade_id
                    }
                    
                    callback_data = {
                        'type': 'button_click',
                        'id': f'confirm_{trade_id}',
                        'phone_number': '+919876543210'
                    }
                    
                    callback_result = await manager.handle_whatsapp_callback(
                        db_session, callback_data
                    )
                    
                    assert callback_result['success'] is True
                    
                    # Verify workflow
                    mock_store.assert_called_once()  # Trade was stored
                    mock_confirm.assert_called_once()  # Trade was confirmed
    
    @pytest.mark.asyncio
    async def test_chart_to_trade_workflow(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test workflow from chart sharing to quick trade"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        with patch.object(manager.chart_generator, 'generate_chart', return_value=b'chart'):
            with patch.object(manager, '_upload_chart_image', return_value='https://chart.url'):
                with patch.object(manager, '_generate_chart_analysis', return_value='Analysis'):
                    with patch.object(manager, '_handle_quick_buy') as mock_quick_buy:
                        
                        # Step 1: Generate and share chart
                        chart_request = WhatsAppChartRequest(
                            symbol="RELIANCE",
                            whatsapp_number="+919876543210",
                            include_trade_buttons=True
                        )
                        
                        chart_result = await manager.generate_whatsapp_chart(
                            db_session, test_user.id, chart_request
                        )
                        
                        assert chart_result['success'] is True
                        assert len(chart_result['trade_buttons']) > 0
                        
                        # Step 2: Simulate quick buy button click
                        mock_quick_buy.return_value = {
                            'success': True,
                            'message': 'Quick buy initiated for RELIANCE'
                        }
                        
                        callback_data = {
                            'type': 'button_click',
                            'id': 'quick_buy_RELIANCE',
                            'phone_number': '+919876543210'
                        }
                        
                        callback_result = await manager.handle_whatsapp_callback(
                            db_session, callback_data
                        )
                        
                        assert callback_result['success'] is True
                        mock_quick_buy.assert_called_once_with(
                            db_session, 'RELIANCE', '+919876543210'
                        )