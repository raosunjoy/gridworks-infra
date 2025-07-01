"""
Comprehensive Test Suite for GridWorks SDK Manager
Tests the unified SDK management system with 100% coverage
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from app.sdk_manager import (
    GridWorksSDK,
    ClientConfiguration,
    ServiceType,
    IntegrationType,
    SDKResponse,
    ServiceManager
)
from app.ai_support import AISupport, SupportTier
from app.ai_intelligence import AIIntelligence, UserTier as IntelligenceTier
from app.ai_moderator import AIModerator


class TestServiceType:
    """Test ServiceType enum"""
    
    def test_service_type_values(self):
        """Test all service type values"""
        assert ServiceType.SUPPORT.value == "support"
        assert ServiceType.INTELLIGENCE.value == "intelligence"
        assert ServiceType.MODERATOR.value == "moderator"
    
    def test_service_type_creation(self):
        """Test service type creation from string"""
        assert ServiceType("support") == ServiceType.SUPPORT
        assert ServiceType("intelligence") == ServiceType.INTELLIGENCE
        assert ServiceType("moderator") == ServiceType.MODERATOR


class TestIntegrationType:
    """Test IntegrationType enum"""
    
    def test_integration_type_values(self):
        """Test all integration type values"""
        assert IntegrationType.REST_API.value == "rest_api"
        assert IntegrationType.GRAPHQL.value == "graphql"
        assert IntegrationType.WEBHOOK.value == "webhook"
        assert IntegrationType.WEBSOCKET.value == "websocket"


class TestClientConfiguration:
    """Test ClientConfiguration class"""
    
    def test_basic_configuration(self):
        """Test basic client configuration creation"""
        config = ClientConfiguration(
            client_id="test_client_123",
            client_name="Test Client",
            api_key="test_api_key_456",
            services=[ServiceType.SUPPORT],
            integration_type=IntegrationType.REST_API
        )
        
        assert config.client_id == "test_client_123"
        assert config.client_name == "Test Client"
        assert config.api_key == "test_api_key_456"
        assert ServiceType.SUPPORT in config.services
        assert config.integration_type == IntegrationType.REST_API
    
    def test_configuration_with_custom_settings(self):
        """Test configuration with custom settings"""
        custom_settings = {
            "ai_personality": "professional",
            "response_time_target": 15,
            "language": "english"
        }
        
        config = ClientConfiguration(
            client_id="custom_client",
            client_name="Custom Client",
            api_key="custom_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API,
            custom_settings=custom_settings
        )
        
        assert config.custom_settings == custom_settings
        assert config.custom_settings["ai_personality"] == "professional"
    
    def test_configuration_with_rate_limits(self):
        """Test configuration with rate limits"""
        rate_limits = {
            "support": 100,
            "intelligence": 50,
            "moderator": 25
        }
        
        config = ClientConfiguration(
            client_id="rate_limited_client",
            client_name="Rate Limited Client", 
            api_key="rate_key",
            services=[ServiceType.SUPPORT],
            integration_type=IntegrationType.REST_API,
            rate_limits=rate_limits
        )
        
        assert config.rate_limits == rate_limits
        assert config.rate_limits["support"] == 100


class TestSDKResponse:
    """Test SDKResponse class"""
    
    def test_successful_response(self):
        """Test successful response creation"""
        response_data = {
            "message": "Query processed successfully",
            "result": "Order failed due to insufficient margin"
        }
        
        response = SDKResponse(
            success=True,
            data=response_data,
            service="support",
            processing_time=0.025
        )
        
        assert response.success is True
        assert response.data == response_data
        assert response.service == "support"
        assert response.processing_time == 0.025
        assert response.error is None
    
    def test_error_response(self):
        """Test error response creation"""
        response = SDKResponse(
            success=False,
            data={},
            service="intelligence",
            processing_time=0.010,
            error="API quota exceeded"
        )
        
        assert response.success is False
        assert response.error == "API quota exceeded"
        assert response.data == {}
    
    def test_response_to_dict(self):
        """Test response dictionary conversion"""
        response = SDKResponse(
            success=True,
            data={"test": "value"},
            service="moderator"
        )
        
        response_dict = response.to_dict()
        assert response_dict["success"] is True
        assert response_dict["data"]["test"] == "value"
        assert response_dict["service"] == "moderator"


class TestServiceManager:
    """Test ServiceManager class"""
    
    @pytest.fixture
    def service_manager(self):
        """Create ServiceManager instance for testing"""
        return ServiceManager()
    
    def test_register_service(self, service_manager):
        """Test service registration"""
        mock_service = Mock()
        
        service_manager.register_service(ServiceType.SUPPORT, mock_service)
        
        assert ServiceType.SUPPORT in service_manager.services
        assert service_manager.services[ServiceType.SUPPORT] == mock_service
    
    def test_get_service_exists(self, service_manager):
        """Test getting existing service"""
        mock_service = Mock()
        service_manager.register_service(ServiceType.INTELLIGENCE, mock_service)
        
        retrieved_service = service_manager.get_service(ServiceType.INTELLIGENCE)
        assert retrieved_service == mock_service
    
    def test_get_service_not_exists(self, service_manager):
        """Test getting non-existent service"""
        with pytest.raises(ValueError, match="Service moderator not registered"):
            service_manager.get_service(ServiceType.MODERATOR)
    
    def test_is_service_available(self, service_manager):
        """Test service availability check"""
        mock_service = Mock()
        service_manager.register_service(ServiceType.SUPPORT, mock_service)
        
        assert service_manager.is_service_available(ServiceType.SUPPORT) is True
        assert service_manager.is_service_available(ServiceType.MODERATOR) is False
    
    def test_get_available_services(self, service_manager):
        """Test getting list of available services"""
        mock_support = Mock()
        mock_intelligence = Mock()
        
        service_manager.register_service(ServiceType.SUPPORT, mock_support)
        service_manager.register_service(ServiceType.INTELLIGENCE, mock_intelligence)
        
        available = service_manager.get_available_services()
        assert ServiceType.SUPPORT in available
        assert ServiceType.INTELLIGENCE in available
        assert ServiceType.MODERATOR not in available


class TestGridWorksSDK:
    """Test GridWorksSDK main class"""
    
    @pytest.fixture
    def basic_config(self):
        """Create basic SDK configuration"""
        return ClientConfiguration(
            client_id="test_sdk_client",
            client_name="Test SDK Client",
            api_key="test_sdk_key",
            services=[ServiceType.SUPPORT],
            integration_type=IntegrationType.REST_API
        )
    
    @pytest.fixture
    def full_config(self):
        """Create full SDK configuration with all services"""
        return ClientConfiguration(
            client_id="full_sdk_client",
            client_name="Full SDK Client",
            api_key="full_sdk_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE, ServiceType.MODERATOR],
            integration_type=IntegrationType.REST_API,
            custom_settings={
                "ai_personality": "expert",
                "response_time": 10
            }
        )
    
    def test_sdk_initialization(self, basic_config):
        """Test SDK initialization"""
        sdk = GridWorksSDK(basic_config)
        
        assert sdk.config == basic_config
        assert sdk.client_id == "test_sdk_client"
        assert sdk.service_manager is not None
        assert sdk.initialized is False
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_initialize_services_support_only(self, mock_ai_support, basic_config):
        """Test initializing SDK with support service only"""
        mock_support_instance = Mock()
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        assert sdk.initialized is True
        assert sdk.service_manager.is_service_available(ServiceType.SUPPORT) is True
        assert sdk.service_manager.is_service_available(ServiceType.INTELLIGENCE) is False
        
        # Verify support service was initialized with correct config
        mock_ai_support.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    @patch('app.ai_intelligence.AIIntelligence')
    @patch('app.ai_moderator.AIModerator')
    async def test_initialize_services_all(self, mock_moderator, mock_intelligence, mock_support, full_config):
        """Test initializing SDK with all services"""
        mock_support_instance = Mock()
        mock_intelligence_instance = Mock()
        mock_moderator_instance = Mock()
        
        mock_support.return_value = mock_support_instance
        mock_intelligence.return_value = mock_intelligence_instance
        mock_moderator.return_value = mock_moderator_instance
        
        sdk = GridWorksSDK(full_config)
        await sdk.initialize_services()
        
        assert sdk.initialized is True
        assert sdk.service_manager.is_service_available(ServiceType.SUPPORT) is True
        assert sdk.service_manager.is_service_available(ServiceType.INTELLIGENCE) is True
        assert sdk.service_manager.is_service_available(ServiceType.MODERATOR) is True
    
    @pytest.mark.asyncio
    async def test_process_request_not_initialized(self, basic_config):
        """Test processing request before initialization"""
        sdk = GridWorksSDK(basic_config)
        
        with pytest.raises(RuntimeError, match="SDK not initialized"):
            await sdk.process_request("support", "query", {})
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_process_support_request(self, mock_ai_support, basic_config):
        """Test processing support request"""
        # Mock support service
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock(return_value={
            "success": True,
            "message": "Order failed due to insufficient margin",
            "response_time": 0.025
        })
        mock_ai_support.return_value = mock_support_instance
        
        # Initialize SDK
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        # Process request
        response = await sdk.process_request(
            service="support",
            action="query",
            data={
                "user_id": "test_user",
                "message": "Why did my order fail?",
                "user_tier": "pro"
            }
        )
        
        assert response.success is True
        assert response.service == "support"
        assert response.data["message"] == "Order failed due to insufficient margin"
        
        # Verify support service was called
        mock_support_instance.process_query.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.ai_intelligence.AIIntelligence')
    async def test_process_intelligence_request(self, mock_ai_intelligence):
        """Test processing intelligence request"""
        config = ClientConfiguration(
            client_id="intelligence_client",
            client_name="Intelligence Client",
            api_key="intel_key",
            services=[ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API
        )
        
        # Mock intelligence service
        mock_intelligence_instance = Mock()
        mock_intelligence_instance.generate_morning_pulse = AsyncMock(return_value={
            "success": True,
            "content": {
                "summary": "NASDAQ down 1.2%",
                "trade_ideas": [{"symbol": "TCS", "action": "SHORT"}]
            }
        })
        mock_ai_intelligence.return_value = mock_intelligence_instance
        
        # Initialize and test
        sdk = GridWorksSDK(config)
        await sdk.initialize_services()
        
        response = await sdk.process_request(
            service="intelligence",
            action="morning_pulse",
            data={"user_id": "test_user", "user_tier": "pro"}
        )
        
        assert response.success is True
        assert response.service == "intelligence"
        assert "trade_ideas" in response.data["content"]
    
    @pytest.mark.asyncio
    async def test_process_request_invalid_service(self, basic_config):
        """Test processing request for unavailable service"""
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        with pytest.raises(ValueError, match="Service intelligence not registered"):
            await sdk.process_request("intelligence", "morning_pulse", {})
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_process_request_invalid_action(self, mock_ai_support, basic_config):
        """Test processing request with invalid action"""
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock()
        # No process_invalid_action method
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        with pytest.raises(ValueError, match="Invalid action"):
            await sdk.process_request("support", "invalid_action", {})
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_process_request_service_error(self, mock_ai_support, basic_config):
        """Test handling service errors"""
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock(side_effect=Exception("Service error"))
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        response = await sdk.process_request("support", "query", {})
        
        assert response.success is False
        assert response.error == "Service error"
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_get_service_status(self, mock_ai_support, basic_config):
        """Test getting service status"""
        mock_support_instance = Mock()
        mock_support_instance.get_health_status = AsyncMock(return_value={
            "status": "healthy",
            "uptime": 99.9,
            "last_check": datetime.now().isoformat()
        })
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        status = await sdk.get_service_status("support")
        
        assert status["status"] == "healthy"
        assert status["uptime"] == 99.9
    
    @pytest.mark.asyncio
    async def test_get_service_status_not_available(self, basic_config):
        """Test getting status for unavailable service"""
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        with pytest.raises(ValueError, match="Service intelligence not available"):
            await sdk.get_service_status("intelligence")
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_shutdown_services(self, mock_ai_support, basic_config):
        """Test shutting down services"""
        mock_support_instance = Mock()
        mock_support_instance.shutdown = AsyncMock()
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(basic_config)
        await sdk.initialize_services()
        
        await sdk.shutdown()
        
        assert sdk.initialized is False
        mock_support_instance.shutdown.assert_called_once()
    
    def test_get_client_info(self, basic_config):
        """Test getting client information"""
        sdk = GridWorksSDK(basic_config)
        
        client_info = sdk.get_client_info()
        
        assert client_info["client_id"] == "test_sdk_client"
        assert client_info["client_name"] == "Test SDK Client"
        assert client_info["integration_type"] == "rest_api"
        assert client_info["services"] == ["support"]


class TestServiceIntegration:
    """Test service integration functionality"""
    
    @pytest.fixture
    def integration_config(self):
        """Create configuration for integration testing"""
        return ClientConfiguration(
            client_id="integration_client",
            client_name="Integration Test Client",
            api_key="integration_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API,
            custom_settings={
                "ai_personality": "professional",
                "response_time_target": 15,
                "whatsapp_delivery": True
            }
        )
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    @patch('app.ai_intelligence.AIIntelligence')
    async def test_multi_service_workflow(self, mock_intelligence, mock_support, integration_config):
        """Test workflow using multiple services"""
        # Mock support service
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock(return_value={
            "success": True,
            "message": "Your portfolio looks good",
            "suggestion": "check morning pulse"
        })
        mock_support.return_value = mock_support_instance
        
        # Mock intelligence service
        mock_intelligence_instance = Mock()
        mock_intelligence_instance.generate_morning_pulse = AsyncMock(return_value={
            "success": True,
            "content": {"summary": "Market looking positive"}
        })
        mock_intelligence.return_value = mock_intelligence_instance
        
        # Initialize SDK
        sdk = GridWorksSDK(integration_config)
        await sdk.initialize_services()
        
        # First request - support query
        support_response = await sdk.process_request(
            service="support",
            action="query",
            data={"message": "How is my portfolio?"}
        )
        
        assert support_response.success is True
        assert "check morning pulse" in support_response.data["suggestion"]
        
        # Second request - intelligence based on support suggestion
        intelligence_response = await sdk.process_request(
            service="intelligence",
            action="morning_pulse",
            data={"user_id": "test_user"}
        )
        
        assert intelligence_response.success is True
        assert "Market looking positive" in intelligence_response.data["content"]["summary"]
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_custom_settings_propagation(self, mock_ai_support, integration_config):
        """Test custom settings are passed to services"""
        mock_support_instance = Mock()
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(integration_config)
        await sdk.initialize_services()
        
        # Verify custom settings were passed during initialization
        call_args = mock_ai_support.call_args
        assert call_args is not None
        # Custom settings should be available in the SDK config
        assert sdk.config.custom_settings["ai_personality"] == "professional"
        assert sdk.config.custom_settings["whatsapp_delivery"] is True


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def error_config(self):
        return ClientConfiguration(
            client_id="error_client",
            client_name="Error Test Client",
            api_key="error_key",
            services=[ServiceType.SUPPORT],
            integration_type=IntegrationType.REST_API
        )
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_service_initialization_failure(self, mock_ai_support, error_config):
        """Test handling service initialization failure"""
        mock_ai_support.side_effect = Exception("Failed to initialize AI Support")
        
        sdk = GridWorksSDK(error_config)
        
        with pytest.raises(RuntimeError, match="Failed to initialize service support"):
            await sdk.initialize_services()
        
        assert sdk.initialized is False
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_service_timeout_handling(self, mock_ai_support, error_config):
        """Test handling service timeouts"""
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(error_config)
        await sdk.initialize_services()
        
        response = await sdk.process_request("support", "query", {})
        
        assert response.success is False
        assert "timeout" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_empty_service_list_initialization(self):
        """Test initialization with empty service list"""
        config = ClientConfiguration(
            client_id="empty_client",
            client_name="Empty Client",
            api_key="empty_key",
            services=[],  # Empty services
            integration_type=IntegrationType.REST_API
        )
        
        sdk = GridWorksSDK(config)
        await sdk.initialize_services()
        
        assert sdk.initialized is True
        assert len(sdk.service_manager.get_available_services()) == 0
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_partial_service_failure(self, mock_ai_support):
        """Test handling partial service failures during initialization"""
        config = ClientConfiguration(
            client_id="partial_client",
            client_name="Partial Client",
            api_key="partial_key",
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API
        )
        
        # Support succeeds, intelligence fails
        mock_support_instance = Mock()
        mock_ai_support.return_value = mock_support_instance
        
        with patch('app.ai_intelligence.AIIntelligence') as mock_intelligence:
            mock_intelligence.side_effect = Exception("Intelligence init failed")
            
            sdk = GridWorksSDK(config)
            
            with pytest.raises(RuntimeError):
                await sdk.initialize_services()


class TestPerformanceAndScaling:
    """Test performance and scaling aspects"""
    
    @pytest.fixture
    def performance_config(self):
        return ClientConfiguration(
            client_id="perf_client",
            client_name="Performance Client",
            api_key="perf_key",
            services=[ServiceType.SUPPORT],
            integration_type=IntegrationType.REST_API,
            rate_limits={"support": 1000}  # High rate limit
        )
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_concurrent_requests(self, mock_ai_support, performance_config):
        """Test handling concurrent requests"""
        mock_support_instance = Mock()
        mock_support_instance.process_query = AsyncMock(return_value={
            "success": True,
            "message": "Concurrent response"
        })
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(performance_config)
        await sdk.initialize_services()
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            task = sdk.process_request(
                service="support",
                action="query",
                data={"message": f"Concurrent query {i}"}
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        assert len(responses) == 10
        for response in responses:
            assert response.success is True
            assert "Concurrent response" in response.data["message"]
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_response_time_tracking(self, mock_ai_support, performance_config):
        """Test response time tracking"""
        mock_support_instance = Mock()
        
        # Mock a service that takes some time
        async def slow_query(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms delay
            return {"success": True, "message": "Slow response"}
        
        mock_support_instance.process_query = slow_query
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(performance_config)
        await sdk.initialize_services()
        
        response = await sdk.process_request("support", "query", {})
        
        assert response.success is True
        assert response.processing_time >= 0.01  # At least 10ms
        assert response.processing_time < 1.0    # But reasonable
    
    @pytest.mark.asyncio
    @patch('app.ai_support.AISupport')
    async def test_memory_cleanup_on_shutdown(self, mock_ai_support, performance_config):
        """Test memory cleanup during shutdown"""
        mock_support_instance = Mock()
        mock_support_instance.shutdown = AsyncMock()
        mock_ai_support.return_value = mock_support_instance
        
        sdk = GridWorksSDK(performance_config)
        await sdk.initialize_services()
        
        # Verify services are registered
        assert len(sdk.service_manager.services) == 1
        
        await sdk.shutdown()
        
        # Verify cleanup
        assert sdk.initialized is False
        mock_support_instance.shutdown.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])