"""
Main GridWorks SDK client
"""

import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import logging

import requests
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import GridWorksConfig, SDKOptions, Environment
from .exceptions import (
    APIError, 
    AuthenticationError, 
    RateLimitError,
    NetworkError,
    TimeoutError,
    ValidationError
)
from .models.common import APIResponse, RequestMetrics
from .ai_suite import AISuiteClient
from .anonymous_services import AnonymousServicesClient  
from .trading import TradingClient
from .banking import BankingClient


class GridWorksSDK:
    """
    Main GridWorks B2B SDK client providing unified access to all services
    """
    
    def __init__(self, config: GridWorksConfig, options: Optional[SDKOptions] = None):
        """
        Initialize the GridWorks SDK
        
        Args:
            config: SDK configuration
            options: Additional SDK options
        """
        self.config = config
        self.options = options or SDKOptions()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize HTTP session
        self.session = requests.Session()
        self._setup_session()
        
        # Request metrics tracking
        self.metrics: List[RequestMetrics] = []
        
        # Initialize service clients
        self.ai_suite = AISuiteClient(self)
        self.anonymous = AnonymousServicesClient(self)
        self.trading = TradingClient(self)
        self.banking = BankingClient(self)
        
        self.logger.info(
            f"GridWorks SDK initialized for environment: {config.environment}",
            extra={"client_id": config.client_id}
        )
    
    def _setup_logging(self):
        """Setup SDK logging"""
        self.logger = logging.getLogger("gridworks_sdk")
        
        if self.options.enable_logging:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, self.options.log_level))
        else:
            self.logger.addHandler(logging.NullHandler())
    
    def _setup_session(self):
        """Setup HTTP session with authentication and headers"""
        # Default headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.options.user_agent,
            "X-Client-ID": self.config.client_id,
            "X-SDK-Version": "1.0.0",
            "X-SDK-Language": "python"
        }
        
        # Authentication headers
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
            
        # Custom headers
        headers.update(self.config.headers)
        
        self.session.headers.update(headers)
        
        # Set timeout
        self.session.timeout = self.config.timeout
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"gw_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def _record_metrics(self, 
                       endpoint: str, 
                       method: str, 
                       duration: float, 
                       status_code: int,
                       request_id: str) -> None:
        """Record request metrics"""
        metrics = RequestMetrics(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.metrics.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def request(self, 
                method: str, 
                endpoint: str, 
                data: Optional[Dict[str, Any]] = None,
                params: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, str]] = None,
                **kwargs) -> APIResponse:
        """
        Make authenticated HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional request arguments
            
        Returns:
            API response
            
        Raises:
            APIError: For API errors
            AuthenticationError: For auth errors
            RateLimitError: For rate limit errors
            NetworkError: For network errors
            TimeoutError: For timeout errors
        """
        request_id = self._generate_request_id()
        start_time = time.time()
        
        # Prepare request
        url = f"{self.config.base_url}{endpoint}"
        request_headers = {}
        if headers:
            request_headers.update(headers)
        request_headers["X-Request-ID"] = request_id
        
        self.logger.debug(
            f"Making {method} request to {endpoint}",
            extra={"request_id": request_id}
        )
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if data else None,
                params=params,
                headers=request_headers,
                **kwargs
            )
            
            duration = time.time() - start_time
            self._record_metrics(endpoint, method, duration, response.status_code, request_id)
            
            # Handle different response codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed", response.text)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Rate limit exceeded", 
                    retry_after=int(retry_after) if retry_after else None
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise APIError(
                        message=error_data.get("message", "API request failed"),
                        status_code=response.status_code,
                        code=error_data.get("code", "API_ERROR"),
                        details=error_data.get("details")
                    )
                except ValueError:
                    raise APIError(
                        message=f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
            
            # Parse successful response
            try:
                response_data = response.json()
                return APIResponse(**response_data)
            except ValueError:
                # Non-JSON response
                return APIResponse(
                    success=True,
                    data=response.text,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    request_id=request_id
                )
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self._record_metrics(endpoint, method, duration, 408, request_id)
            raise TimeoutError(f"Request timeout after {self.config.timeout}s")
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time  
            self._record_metrics(endpoint, method, duration, 0, request_id)
            raise NetworkError(f"Network error: {str(e)}")
        except Exception as e:
            duration = time.time() - start_time
            self._record_metrics(endpoint, method, duration, 500, request_id)
            if isinstance(e, (APIError, AuthenticationError, RateLimitError)):
                raise
            raise APIError(f"Unexpected error: {str(e)}")
    
    async def async_request(self,
                           method: str,
                           endpoint: str, 
                           data: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None,
                           **kwargs) -> APIResponse:
        """
        Make async authenticated HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters  
            headers: Additional headers
            **kwargs: Additional request arguments
            
        Returns:
            API response
        """
        request_id = self._generate_request_id()
        start_time = time.time()
        
        url = f"{self.config.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        request_headers["X-Request-ID"] = request_id
        
        self.logger.debug(
            f"Making async {method} request to {endpoint}",
            extra={"request_id": request_id}
        )
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    **kwargs
                ) as response:
                    duration = time.time() - start_time
                    self._record_metrics(endpoint, method, duration, response.status, request_id)
                    
                    if response.status == 401:
                        raise AuthenticationError("Authentication failed")
                    elif response.status == 429:
                        retry_after = response.headers.get("Retry-After")
                        raise RateLimitError(
                            "Rate limit exceeded",
                            retry_after=int(retry_after) if retry_after else None
                        )
                    elif response.status >= 400:
                        error_text = await response.text()
                        try:
                            error_data = await response.json()
                            raise APIError(
                                message=error_data.get("message", "API request failed"),
                                status_code=response.status,
                                code=error_data.get("code", "API_ERROR"),
                                details=error_data.get("details")
                            )
                        except:
                            raise APIError(
                                message=f"HTTP {response.status}: {error_text}",
                                status_code=response.status
                            )
                    
                    # Parse successful response
                    try:
                        response_data = await response.json()
                        return APIResponse(**response_data)
                    except:
                        response_text = await response.text()
                        return APIResponse(
                            success=True,
                            data=response_text,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            request_id=request_id
                        )
                        
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self._record_metrics(endpoint, method, duration, 408, request_id)
            raise TimeoutError(f"Request timeout after {self.config.timeout}s")
        except aiohttp.ClientError as e:
            duration = time.time() - start_time
            self._record_metrics(endpoint, method, duration, 0, request_id)
            raise NetworkError(f"Network error: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Test API connectivity
        
        Returns:
            True if API is healthy
        """
        try:
            response = self.request("GET", "/health")
            return response.success
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    def get_client_info(self) -> APIResponse:
        """Get current client information"""
        return self.request("GET", "/api/v1/client/info")
    
    def get_metrics(self) -> List[RequestMetrics]:
        """Get request metrics"""
        return self.metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear request metrics"""
        self.metrics.clear()
    
    def update_config(self, **kwargs) -> None:
        """
        Update SDK configuration
        
        Args:
            **kwargs: Configuration updates
        """
        # Update config
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Re-setup session if needed
        if any(key in kwargs for key in ['token', 'api_key', 'headers']):
            self._setup_session()
        
        self.logger.info("SDK configuration updated")
    
    @classmethod
    def create_for_environment(cls,
                              environment: Environment,
                              api_key: str,
                              client_id: str,
                              options: Optional[SDKOptions] = None) -> "GridWorksSDK":
        """
        Create SDK instance for specific environment
        
        Args:
            environment: Target environment
            api_key: GridWorks API key
            client_id: Client identifier
            options: Additional SDK options
            
        Returns:
            Configured SDK instance
        """
        from .config import create_config_for_environment
        
        config = create_config_for_environment(environment, api_key, client_id)
        return cls(config, options)
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key format
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        import re
        pattern = r'^gw_(dev|stg|prod)_[a-zA-Z0-9]{32}$'
        return bool(re.match(pattern, api_key))
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close()
    
    def close(self):
        """Close HTTP session"""
        self.session.close()