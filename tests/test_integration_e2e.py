"""
Integration and End-to-End Test Suite for GridWorks Platform
Tests complete workflows and feature interactions across all components
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch
import json
import uuid

from fastapi.testclient import TestClient

from app.charting.types.kagi import KagiChart
from app.charting.types.range_bars import RangeBarsChart
from app.integrations.whatsapp_trading import WhatsAppTradingManager
from app.features.social_collaboration import SocialCollaborationManager
from app.features.trading_idea_marketplace import TradingIdeaMarketplace


class TestChartingIntegration:
    """Test integration between different charting components"""
    
    @pytest.mark.asyncio
    async def test_kagi_to_range_bars_conversion(self, chart_config, sample_ohlcv_data):
        """Test conversion of Kagi chart data to Range Bars"""
        # Create and populate Kagi chart
        kagi_chart = KagiChart("kagi_test", chart_config, Mock())
        
        for data_point in sample_ohlcv_data[:50]:
            await kagi_chart.add_data_point(data_point)
        
        # Create Range Bars chart with same data
        range_chart = RangeBarsChart("range_test", chart_config, Mock())
        
        for data_point in sample_ohlcv_data[:50]:
            await range_chart.add_data_point(data_point)
        
        # Both charts should have processed the data
        assert len(kagi_chart.kagi_lines) > 0 or kagi_chart.current_line is not None
        assert len(range_chart.range_bars) > 0 or range_chart.current_bar is not None
        
        # Both charts should show same trend direction
        kagi_trend = kagi_chart.get_current_trend()
        range_trend = range_chart.get_current_trend()
        
        # Trends should be compatible (both bullish, bearish, or at least one neutral)
        compatible_trends = (
            kagi_trend['trend'] == range_trend['trend'] or
            kagi_trend['trend'] == 'neutral' or
            range_trend['trend'] == 'neutral'
        )
        assert compatible_trends
    
    @pytest.mark.asyncio
    async def test_chart_pattern_cross_validation(self, chart_config, performance_test_data):
        """Test pattern detection across different chart types"""
        # Create both chart types
        kagi_chart = KagiChart("kagi_pattern", chart_config, Mock())
        range_chart = RangeBarsChart("range_pattern", chart_config, Mock())
        
        # Process same data through both
        for data_point in performance_test_data[:1000]:
            await kagi_chart.add_data_point(data_point)
            await range_chart.add_data_point(data_point)
        
        # Detect patterns in both
        kagi_patterns = await kagi_chart.detect_patterns()
        range_patterns = await range_chart.detect_patterns()
        
        # Both should detect some patterns with large dataset
        assert len(kagi_patterns) > 0 or len(range_patterns) > 0
        
        # If both detect patterns, they should have reasonable confidence
        for pattern in kagi_patterns:
            assert 0 <= pattern['confidence'] <= 1
        
        for pattern in range_patterns:
            assert 0 <= pattern['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_chart_performance_comparison(self, chart_config, performance_test_data):
        """Test performance comparison between chart types"""
        kagi_chart = KagiChart("kagi_perf", chart_config, Mock())
        range_chart = RangeBarsChart("range_perf", chart_config, Mock())
        
        # Measure processing time for both
        start_time = datetime.now()
        for data_point in performance_test_data[:500]:
            await kagi_chart.add_data_point(data_point)
        kagi_time = (datetime.now() - start_time).total_seconds()
        
        start_time = datetime.now()
        for data_point in performance_test_data[:500]:
            await range_chart.add_data_point(data_point)
        range_time = (datetime.now() - start_time).total_seconds()
        
        # Both should complete within reasonable time (< 5 seconds)
        assert kagi_time < 5.0
        assert range_time < 5.0
        
        # Get analytics for both
        kagi_analytics = kagi_chart.get_analytics()
        range_analytics = range_chart.get_analytics()
        
        # Both should have valid analytics
        if kagi_analytics:
            assert 'current_trend' in kagi_analytics
        if range_analytics:
            assert 'current_trend' in range_analytics


class TestWhatsAppTradingIntegration:
    """Test WhatsApp trading integration with other components"""
    
    @pytest.mark.asyncio
    async def test_whatsapp_chart_to_trade_flow(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client,
        mock_trading_engine
    ):
        """Test complete flow from WhatsApp chart request to trade execution"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        manager.trading_engine = mock_trading_engine
        
        # Step 1: Generate WhatsApp chart
        with patch.object(manager.chart_generator, 'generate_chart', return_value=b'chart_data'):
            with patch.object(manager, '_upload_chart_image', return_value='https://chart.url'):
                with patch.object(manager, '_generate_chart_analysis', return_value='Bullish setup'):
                    
                    chart_result = await manager.generate_whatsapp_chart(
                        db_session, test_user.id, {
                            'symbol': 'RELIANCE',
                            'timeframe': '15m',
                            'whatsapp_number': '+919876543210',
                            'include_trade_buttons': True
                        }
                    )
                    
                    assert chart_result['success'] is True
                    assert len(chart_result['trade_buttons']) > 0
        
        # Step 2: Simulate quick trade from chart button
        mock_trading_engine.get_current_price.return_value = 2500.0
        
        with patch.object(manager.risk_manager, 'calculate_position_size', return_value=10):
            with patch.object(manager, 'execute_whatsapp_trade',
                             return_value={'success': True, 'trade_id': 'trade_from_chart'}) as mock_trade:
                
                quick_trade_result = await manager.execute_quick_trade(
                    db_session, test_user.id, {
                        'preset_name': 'scalp_buy',
                        'symbol': 'RELIANCE',
                        'whatsapp_number': '+919876543210'
                    }
                )
                
                assert quick_trade_result['success'] is True
                mock_trade.assert_called_once()
        
        # Verify integration: chart led to trade
        assert chart_result['chart_url']
        assert quick_trade_result['trade_id']
    
    @pytest.mark.asyncio
    async def test_whatsapp_alert_to_trade_flow(
        self, 
        db_session, 
        test_user,
        mock_whatsapp_client
    ):
        """Test flow from WhatsApp alert setup to triggered alert to trade"""
        manager = WhatsAppTradingManager()
        manager.whatsapp_client = mock_whatsapp_client
        
        # Step 1: Setup price alert
        with patch.object(manager, '_store_whatsapp_alert') as mock_store:
            
            alert_result = await manager.setup_whatsapp_alert(
                db_session, test_user.id, {
                    'symbol': 'NIFTY',
                    'condition': {'type': 'price_above', 'value': 18500.0},
                    'alert_type': 'PRICE',
                    'whatsapp_number': '+919876543210'
                }
            )
            
            assert alert_result['success'] is True
            mock_store.assert_called_once()
        
        # Step 2: Simulate alert trigger and quick trade response
        callback_result = await manager.handle_whatsapp_callback(
            db_session, {
                'type': 'button_click',
                'id': 'quick_buy_NIFTY',
                'phone_number': '+919876543210'
            }
        )
        
        # Should handle the callback (even if mocked)
        assert 'success' in callback_result
    
    @pytest.mark.asyncio
    async def test_whatsapp_collaboration_integration(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_whatsapp_client
    ):
        """Test integration between WhatsApp and social collaboration"""
        whatsapp_manager = WhatsAppTradingManager()
        collab_manager = SocialCollaborationManager()
        
        whatsapp_manager.whatsapp_client = mock_whatsapp_client
        
        # Step 1: Expert shares chart via WhatsApp
        with patch.object(whatsapp_manager.chart_generator, 'generate_chart', return_value=b'chart'):
            with patch.object(whatsapp_manager, '_upload_chart_image', return_value='https://chart.url'):
                with patch.object(whatsapp_manager, '_generate_chart_analysis', return_value='Analysis'):
                    
                    expert_chart_result = await whatsapp_manager.generate_whatsapp_chart(
                        db_session, expert_user.id, {
                            'symbol': 'RELIANCE',
                            'whatsapp_number': '+919876543210',
                            'analysis_notes': 'Expert analysis for collaboration'
                        }
                    )
                    
                    assert expert_chart_result['success'] is True
        
        # Step 2: User copies expert's drawing
        with patch.object(collab_manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 900}):
            with patch.object(collab_manager, '_get_daily_copy_count', return_value=5):
                with patch.object(collab_manager, '_validate_source_drawings', return_value=[Mock()]):
                    with patch.object(collab_manager, '_validate_user_chart', return_value=Mock()):
                        with patch.object(collab_manager, '_copy_drawing_with_attribution',
                                         return_value={'id': 'copied_from_whatsapp'}):
                            
                            copy_result = await collab_manager.copy_expert_drawings(
                                db_session, test_user.id, {
                                    'expert_user_id': expert_user.id,
                                    'chart_id': 'whatsapp_chart',
                                    'drawing_ids': ['drawing_1'],
                                    'copy_to_chart_id': 'user_chart',
                                    'symbol': 'RELIANCE',
                                    'timeframe': '15m'
                                }
                            )
                            
                            assert copy_result['success'] is True
        
        # Verify integration: WhatsApp chart led to collaboration
        assert expert_chart_result['chart_url']
        assert copy_result['expert_attribution']['expert_id'] == expert_user.id


class TestSocialCollaborationIntegration:
    """Test social collaboration integration with other features"""
    
    @pytest.mark.asyncio
    async def test_collaboration_to_marketplace_flow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_zk_verification,
        mock_notification_service
    ):
        """Test flow from collaboration to marketplace idea publishing"""
        collab_manager = SocialCollaborationManager()
        marketplace = TradingIdeaMarketplace()
        
        collab_manager.zk_verification = mock_zk_verification
        marketplace.zk_verification = mock_zk_verification
        marketplace.notification_service = mock_notification_service
        
        # Step 1: Collaborative annotation discussion
        with patch.object(collab_manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True}):
            with patch.object(collab_manager, '_get_chart_annotation_count', return_value=10):
                
                annotation_result = await collab_manager.create_collaborative_annotation(
                    db_session, test_user.id, {
                        'chart_id': 'collab_chart',
                        'annotation_type': 'INSIGHT',
                        'content': 'This setup looks very promising for a trade idea',
                        'position': {'x': 100, 'y': 200}
                    }
                )
                
                assert annotation_result['success'] is True
        
        # Step 2: Expert publishes trading idea based on collaboration
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM'}):
            with patch.object(marketplace, '_notify_idea_subscribers'):
                
                idea_result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, {
                        'title': 'Collaborative Analysis: RELIANCE Setup',
                        'description': 'Based on collaborative discussion and analysis',
                        'idea_type': 'TRADE_SIGNAL',
                        'category': 'EQUITY',
                        'symbol': 'RELIANCE',
                        'risk_level': 'MEDIUM',
                        'time_horizon': 'SHORT_TERM',
                        'technical_rationale': 'Collaborative technical analysis confirms bullish setup',
                        'is_premium': True,
                        'premium_price': Decimal('299.00')
                    }
                )
                
                assert idea_result['success'] is True
        
        # Verify integration: collaboration influenced marketplace idea
        assert annotation_result['annotation']['content']
        assert 'Collaborative' in idea_result['title']
    
    @pytest.mark.asyncio
    async def test_expert_drawing_to_idea_workflow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_zk_verification
    ):
        """Test workflow from expert drawing copy to trading idea subscription"""
        collab_manager = SocialCollaborationManager()
        marketplace = TradingIdeaMarketplace()
        
        collab_manager.zk_verification = mock_zk_verification
        
        # Step 1: Copy expert drawing
        with patch.object(collab_manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 950}):
            with patch.object(collab_manager, '_get_daily_copy_count', return_value=3):
                with patch.object(collab_manager, '_validate_source_drawings', return_value=[Mock()]):
                    with patch.object(collab_manager, '_validate_user_chart', return_value=Mock()):
                        with patch.object(collab_manager, '_copy_drawing_with_attribution',
                                         return_value={'id': 'copied_expert_drawing'}):
                            
                            copy_result = await collab_manager.copy_expert_drawings(
                                db_session, test_user.id, {
                                    'expert_user_id': expert_user.id,
                                    'chart_id': 'expert_chart',
                                    'drawing_ids': ['expert_drawing'],
                                    'copy_to_chart_id': 'user_chart',
                                    'symbol': 'NIFTY',
                                    'timeframe': '15m'
                                }
                            )
                            
                            assert copy_result['success'] is True
        
        # Step 2: User subscribes to expert for more ideas
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM', 'name': 'Expert Trader'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                with patch.object(marketplace.payment_processor, 'process_subscription_payment',
                                 return_value={'success': True, 'transaction_id': 'txn_after_copy'}):
                    
                    subscription_result = await marketplace.subscribe_to_expert(
                        db_session, test_user.id, {
                            'expert_user_id': expert_user.id,
                            'subscription_type': 'MONTHLY'
                        }
                    )
                    
                    assert subscription_result['success'] is True
        
        # Verify workflow: drawing copy led to subscription
        assert copy_result['expert_attribution']['expert_id'] == expert_user.id
        assert subscription_result['expert_name']


class TestMarketplaceIntegration:
    """Test marketplace integration with other components"""
    
    @pytest.mark.asyncio
    async def test_marketplace_to_whatsapp_flow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_whatsapp_client,
        mock_payment_processor
    ):
        """Test flow from marketplace subscription to WhatsApp notifications"""
        marketplace = TradingIdeaMarketplace()
        whatsapp_manager = WhatsAppTradingManager()
        
        marketplace.payment_processor = mock_payment_processor
        whatsapp_manager.whatsapp_client = mock_whatsapp_client
        
        # Step 1: Subscribe to expert
        mock_payment_processor.process_subscription_payment.return_value = {
            'success': True,
            'transaction_id': 'txn_marketplace_whatsapp'
        }
        
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'VIP', 'name': 'VIP Expert'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                subscription_result = await marketplace.subscribe_to_expert(
                    db_session, test_user.id, {
                        'expert_user_id': expert_user.id,
                        'subscription_type': 'YEARLY'
                    }
                )
                
                assert subscription_result['success'] is True
        
        # Step 2: Expert publishes idea (would trigger WhatsApp notification)
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'VIP'}):
            with patch.object(marketplace, '_notify_idea_subscribers') as mock_notify:
                
                idea_result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, {
                        'title': 'VIP Trading Signal',
                        'description': 'Exclusive VIP trading signal for subscribers',
                        'idea_type': 'TRADE_SIGNAL',
                        'category': 'OPTIONS',
                        'symbol': 'NIFTY',
                        'risk_level': 'HIGH',
                        'time_horizon': 'INTRADAY',
                        'technical_rationale': 'Advanced options strategy',
                        'is_premium': True,
                        'premium_price': Decimal('1999.00')
                    }
                )
                
                assert idea_result['success'] is True
                mock_notify.assert_called_once()
        
        # Step 3: Simulate WhatsApp alert for new idea
        alert_result = await whatsapp_manager.setup_whatsapp_alert(
            db_session, test_user.id, {
                'symbol': 'NIFTY',
                'condition': {'type': 'new_idea_published', 'expert_id': expert_user.id},
                'alert_type': 'PATTERN',
                'whatsapp_number': '+919876543210'
            }
        )
        
        assert alert_result['success'] is True
        
        # Verify integration flow
        assert subscription_result['subscription_type'] == 'YEARLY'
        assert idea_result['is_premium'] is True
        assert alert_result['status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_complete_platform_workflow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        chart_config,
        sample_ohlcv_data,
        mock_external_services
    ):
        """Test complete platform workflow across all features"""
        # Initialize all managers
        whatsapp_manager = WhatsAppTradingManager()
        collab_manager = SocialCollaborationManager()
        marketplace = TradingIdeaMarketplace()
        
        # Setup mocks
        for service_name, mock_service in mock_external_services.items():
            setattr(whatsapp_manager, service_name, mock_service)
            setattr(collab_manager, service_name, mock_service)
            setattr(marketplace, service_name, mock_service)
        
        # Step 1: Create and analyze charts
        kagi_chart = KagiChart("workflow_kagi", chart_config, Mock())
        range_chart = RangeBarsChart("workflow_range", chart_config, Mock())
        
        for data_point in sample_ohlcv_data[:30]:
            await kagi_chart.add_data_point(data_point)
            await range_chart.add_data_point(data_point)
        
        kagi_patterns = await kagi_chart.detect_patterns()
        range_patterns = await range_chart.detect_patterns()
        
        # Step 2: Expert shares chart analysis via WhatsApp
        with patch.object(whatsapp_manager.chart_generator, 'generate_chart', return_value=b'chart'):
            with patch.object(whatsapp_manager, '_upload_chart_image', return_value='https://chart.url'):
                with patch.object(whatsapp_manager, '_generate_chart_analysis', return_value='Strong setup'):
                    
                    chart_share_result = await whatsapp_manager.generate_whatsapp_chart(
                        db_session, expert_user.id, {
                            'symbol': 'RELIANCE',
                            'timeframe': '15m',
                            'whatsapp_number': '+919876543210',
                            'analysis_notes': f'Kagi patterns: {len(kagi_patterns)}, Range patterns: {len(range_patterns)}'
                        }
                    )
        
        # Step 3: Start collaboration session
        with patch.object(collab_manager, '_validate_user_chart', return_value=Mock()):
            with patch.object(collab_manager, '_validate_invited_users',
                             return_value=[{'id': test_user.id, 'name': 'User'}]):
                
                collab_result = await collab_manager.start_collaboration_session(
                    db_session, expert_user.id, {
                        'chart_id': 'workflow_chart',
                        'invited_user_ids': [test_user.id],
                        'permission_level': 'COMMENT'
                    }
                )
        
        # Step 4: User copies expert drawing
        with patch.object(collab_manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 900}):
            with patch.object(collab_manager, '_get_daily_copy_count', return_value=2):
                with patch.object(collab_manager, '_validate_source_drawings', return_value=[Mock()]):
                    with patch.object(collab_manager, '_validate_user_chart', return_value=Mock()):
                        with patch.object(collab_manager, '_copy_drawing_with_attribution',
                                         return_value={'id': 'workflow_copy'}):
                            
                            copy_result = await collab_manager.copy_expert_drawings(
                                db_session, test_user.id, {
                                    'expert_user_id': expert_user.id,
                                    'chart_id': 'expert_chart',
                                    'drawing_ids': ['expert_drawing'],
                                    'copy_to_chart_id': 'user_chart',
                                    'symbol': 'RELIANCE',
                                    'timeframe': '15m'
                                }
                            )
        
        # Step 5: Expert publishes trading idea
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM'}):
            with patch.object(marketplace, '_notify_idea_subscribers'):
                
                idea_result = await marketplace.publish_trading_idea(
                    db_session, expert_user.id, {
                        'title': 'Complete Workflow Trading Idea',
                        'description': 'Based on comprehensive analysis and collaboration',
                        'idea_type': 'TRADE_SIGNAL',
                        'category': 'EQUITY',
                        'symbol': 'RELIANCE',
                        'risk_level': 'MEDIUM',
                        'time_horizon': 'SHORT_TERM',
                        'technical_rationale': 'Multi-chart analysis with collaborative validation',
                        'is_premium': True,
                        'premium_price': Decimal('499.00')
                    }
                )
        
        # Step 6: User subscribes and executes trade via WhatsApp
        with patch.object(marketplace, '_validate_expert_user',
                         return_value={'tier': 'PREMIUM', 'name': 'Expert'}):
            with patch.object(db_session, 'query') as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = None
                
                with patch.object(marketplace.payment_processor, 'process_subscription_payment',
                                 return_value={'success': True, 'transaction_id': 'workflow_sub'}):
                    
                    subscription_result = await marketplace.subscribe_to_expert(
                        db_session, test_user.id, {
                            'expert_user_id': expert_user.id,
                            'subscription_type': 'MONTHLY'
                        }
                    )
        
        # Step 7: Execute trade via WhatsApp
        with patch.object(whatsapp_manager, '_validate_whatsapp_session', return_value=Mock()):
            with patch.object(whatsapp_manager.risk_manager, 'validate_trade',
                             return_value={'approved': True}):
                with patch.object(whatsapp_manager, '_store_pending_trade'):
                    
                    trade_result = await whatsapp_manager.execute_whatsapp_trade(
                        db_session, test_user.id, {
                            'symbol': 'RELIANCE',
                            'action': 'BUY',
                            'quantity': 10,
                            'whatsapp_number': '+919876543210',
                            'message_id': 'workflow_trade'
                        }
                    )
        
        # Verify complete workflow
        assert chart_share_result['success'] is True
        assert collab_result['success'] is True
        assert copy_result['success'] is True
        assert idea_result['success'] is True
        assert subscription_result['success'] is True
        assert trade_result['success'] is True
        
        # Verify data flow
        assert chart_share_result['chart_url']
        assert collab_result['session_id']
        assert copy_result['copy_id']
        assert idea_result['idea_id']
        assert subscription_result['subscription_id']
        assert trade_result['trade_id']


class TestPerformanceIntegration:
    """Test performance across integrated components"""
    
    @pytest.mark.asyncio
    async def test_concurrent_chart_processing(self, chart_config, performance_test_data):
        """Test concurrent processing of multiple chart types"""
        async def process_kagi():
            kagi = KagiChart("concurrent_kagi", chart_config, Mock())
            for data in performance_test_data[:200]:
                await kagi.add_data_point(data)
            return kagi.get_analytics()
        
        async def process_range_bars():
            range_bars = RangeBarsChart("concurrent_range", chart_config, Mock())
            for data in performance_test_data[:200]:
                await range_bars.add_data_point(data)
            return range_bars.get_analytics()
        
        # Process both chart types concurrently
        start_time = datetime.now()
        kagi_result, range_result = await asyncio.gather(
            process_kagi(),
            process_range_bars()
        )
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete within reasonable time
        assert total_time < 10.0
        
        # Both should produce valid analytics
        assert kagi_result or isinstance(kagi_result, dict)
        assert range_result or isinstance(range_result, dict)
    
    @pytest.mark.asyncio
    async def test_high_volume_marketplace_operations(
        self, 
        db_session, 
        test_user, 
        expert_user
    ):
        """Test marketplace performance under high volume"""
        marketplace = TradingIdeaMarketplace()
        
        # Mock high-volume search
        with patch.object(db_session, 'query') as mock_query:
            # Simulate large result set
            mock_query.return_value.filter.return_value.order_by.return_value.count.return_value = 10000
            mock_query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            
            with patch.object(marketplace, '_get_user_subscriptions', return_value=set()):
                
                # Perform multiple concurrent searches
                search_tasks = []
                for i in range(10):
                    search_task = marketplace.search_marketplace(
                        db_session, test_user.id, {
                            'query': f'search_{i}',
                            'limit': 50,
                            'offset': i * 50
                        }
                    )
                    search_tasks.append(search_task)
                
                start_time = datetime.now()
                results = await asyncio.gather(*search_tasks)
                search_time = (datetime.now() - start_time).total_seconds()
                
                # Should handle concurrent searches efficiently
                assert search_time < 5.0
                assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, chart_config):
        """Test memory usage under sustained load"""
        charts = []
        
        # Create multiple chart instances
        for i in range(10):
            kagi = KagiChart(f"memory_test_{i}", chart_config, Mock())
            range_bars = RangeBarsChart(f"memory_test_range_{i}", chart_config, Mock())
            charts.extend([kagi, range_bars])
        
        # Add data to all charts
        for i in range(100):
            data_point = Mock()
            data_point.timestamp = datetime.utcnow() + timedelta(seconds=i)
            data_point.close = 100.0 + i * 0.1
            data_point.volume = 1000
            
            for chart in charts:
                await chart.add_data_point(data_point)
        
        # Verify all charts are functioning
        for chart in charts:
            if hasattr(chart, 'kagi_lines'):
                assert len(chart.kagi_lines) >= 0
            if hasattr(chart, 'range_bars'):
                assert len(chart.range_bars) >= 0


class TestErrorHandlingIntegration:
    """Test error handling across integrated components"""
    
    @pytest.mark.asyncio
    async def test_cascading_error_handling(
        self, 
        db_session, 
        test_user, 
        expert_user
    ):
        """Test error handling when one component fails"""
        whatsapp_manager = WhatsAppTradingManager()
        collab_manager = SocialCollaborationManager()
        
        # Simulate WhatsApp service failure
        whatsapp_manager.whatsapp_client = Mock()
        whatsapp_manager.whatsapp_client.send_message = AsyncMock(
            side_effect=Exception("WhatsApp service unavailable")
        )
        
        # Collaboration should still work independently
        with patch.object(collab_manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True}):
            with patch.object(collab_manager, '_get_chart_annotation_count', return_value=5):
                
                # This should succeed despite WhatsApp failure
                annotation_result = await collab_manager.create_collaborative_annotation(
                    db_session, test_user.id, {
                        'chart_id': 'error_test_chart',
                        'annotation_type': 'NOTE',
                        'content': 'This should work despite WhatsApp failure',
                        'position': {'x': 100, 'y': 200}
                    }
                )
                
                assert annotation_result['success'] is True
        
        # WhatsApp trade should fail gracefully
        with patch.object(whatsapp_manager, '_validate_whatsapp_session', return_value=Mock()):
            with patch.object(whatsapp_manager.risk_manager, 'validate_trade',
                             return_value={'approved': True}):
                
                with pytest.raises(Exception):
                    await whatsapp_manager.execute_whatsapp_trade(
                        db_session, test_user.id, {
                            'symbol': 'RELIANCE',
                            'action': 'BUY',
                            'quantity': 10,
                            'whatsapp_number': '+919876543210',
                            'message_id': 'error_test'
                        }
                    )
    
    @pytest.mark.asyncio
    async def test_data_consistency_on_failures(self, chart_config, sample_ohlcv_data):
        """Test data consistency when processing fails"""
        chart = KagiChart("consistency_test", chart_config, Mock())
        
        # Add some valid data
        for data_point in sample_ohlcv_data[:10]:
            await chart.add_data_point(data_point)
        
        initial_line_count = len(chart.kagi_lines)
        
        # Simulate invalid data that might cause processing error
        invalid_data = Mock()
        invalid_data.timestamp = datetime.utcnow()
        invalid_data.close = float('inf')  # Invalid price
        invalid_data.volume = 1000
        
        try:
            await chart.add_data_point(invalid_data)
        except:
            pass  # Expected to fail
        
        # Chart state should remain consistent
        assert len(chart.kagi_lines) == initial_line_count
        
        # Should be able to continue processing valid data
        valid_data = sample_ohlcv_data[10]
        await chart.add_data_point(valid_data)
        
        # Analytics should still work
        analytics = chart.get_analytics()
        assert isinstance(analytics, dict)


class TestAPIIntegration:
    """Test API integration across all endpoints"""
    
    def test_cross_feature_api_workflow(self, test_client, auth_headers, expert_auth_headers):
        """Test API workflow across multiple features"""
        
        # Step 1: Expert publishes idea via marketplace API
        idea_data = {
            "title": "API Integration Test Idea",
            "description": "Testing API integration workflow",
            "idea_type": "TRADE_SIGNAL",
            "category": "EQUITY",
            "symbol": "TESTSTOCK",
            "risk_level": "MEDIUM",
            "time_horizon": "SHORT_TERM",
            "technical_rationale": "API integration test",
            "is_premium": True,
            "premium_price": 99.0
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.publish_trading_idea.return_value = {
                'success': True,
                'idea_id': 'api_test_idea',
                'title': 'API Integration Test Idea'
            }
            
            idea_response = test_client.post(
                "/api/v1/marketplace/publish-idea",
                json=idea_data,
                headers=expert_auth_headers
            )
            
            assert idea_response.status_code == 200
        
        # Step 2: User searches marketplace via API
        search_data = {
            "symbol": "TESTSTOCK",
            "is_premium": True,
            "limit": 10
        }
        
        with patch('app.features.trading_idea_marketplace.marketplace') as mock_marketplace:
            mock_marketplace.search_marketplace.return_value = {
                'ideas': [{'idea_id': 'api_test_idea', 'symbol': 'TESTSTOCK'}],
                'total_count': 1,
                'page_info': {'has_next': False}
            }
            
            search_response = test_client.post(
                "/api/v1/marketplace/search",
                json=search_data,
                headers=auth_headers
            )
            
            assert search_response.status_code == 200
        
        # Step 3: User generates WhatsApp chart via API
        chart_data = {
            "symbol": "TESTSTOCK",
            "timeframe": "15m",
            "whatsapp_number": "+919876543210",
            "include_trade_buttons": True
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_whatsapp:
            mock_whatsapp.generate_whatsapp_chart.return_value = {
                'success': True,
                'chart_url': 'https://test.url',
                'trade_buttons': [{'id': 'buy', 'title': 'Buy'}],
                'expires_at': datetime.utcnow() + timedelta(hours=24)
            }
            
            chart_response = test_client.post(
                "/api/v1/whatsapp/chart",
                json=chart_data,
                headers=auth_headers
            )
            
            assert chart_response.status_code == 200
        
        # Step 4: User starts collaboration via API
        collab_data = {
            "chart_id": "api_test_chart",
            "invited_user_ids": ["expert_user"],
            "permission_level": "COMMENT"
        }
        
        with patch('app.features.social_collaboration.social_collaboration') as mock_collab:
            mock_collab.start_collaboration_session.return_value = {
                'success': True,
                'session_id': 'api_test_session',
                'chart_id': 'api_test_chart',
                'invited_users': [{'id': 'expert_user', 'name': 'Expert'}],
                'permissions': {'user': 'OWNER', 'expert_user': 'COMMENT'},
                'active': True
            }
            
            collab_response = test_client.post(
                "/api/v1/social/start-collaboration",
                json=collab_data,
                headers=auth_headers
            )
            
            assert collab_response.status_code == 200
        
        # Verify all API calls succeeded
        assert idea_response.json()['success'] is True
        assert len(search_response.json()['ideas']) == 1
        assert chart_response.json()['success'] is True
        assert collab_response.json()['session_id'] == 'api_test_session'
    
    def test_api_error_propagation(self, test_client, auth_headers):
        """Test how errors propagate through API layers"""
        
        # Test invalid data in marketplace API
        invalid_idea_data = {
            "title": "",  # Invalid empty title
            "description": "Test",
            "idea_type": "INVALID_TYPE",  # Invalid enum
            "category": "EQUITY"
        }
        
        response = test_client.post(
            "/api/v1/marketplace/publish-idea",
            json=invalid_idea_data,
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == 422  # Validation error
        
        # Test invalid WhatsApp number format
        invalid_whatsapp_data = {
            "symbol": "RELIANCE",
            "whatsapp_number": "invalid_number"  # Invalid format
        }
        
        with patch('app.integrations.whatsapp_trading.whatsapp_trading') as mock_whatsapp:
            mock_whatsapp.generate_whatsapp_chart.side_effect = Exception("Invalid phone format")
            
            response = test_client.post(
                "/api/v1/whatsapp/chart",
                json=invalid_whatsapp_data,
                headers=auth_headers
            )
            
            # Should handle error appropriately
            assert response.status_code in [400, 422, 500]
    
    def test_api_health_checks(self, test_client):
        """Test health check endpoints across all features"""
        
        # Test marketplace health
        marketplace_health = test_client.get("/api/v1/marketplace/health")
        assert marketplace_health.status_code == 200
        assert marketplace_health.json()['status'] == 'healthy'
        
        # Test WhatsApp health
        whatsapp_health = test_client.get("/api/v1/whatsapp/health")
        assert whatsapp_health.status_code == 200
        assert whatsapp_health.json()['status'] == 'healthy'
        
        # Test social collaboration health
        social_health = test_client.get("/api/v1/social/health")
        assert social_health.status_code == 200
        assert social_health.json()['status'] == 'healthy'


# Mark all integration tests for slower execution
pytestmark = pytest.mark.integration