"""
GridWorks B2B Infrastructure Services SDK for Python

This SDK provides comprehensive access to all GridWorks B2B services:
- AI Suite: Multi-language support, market intelligence, content moderation
- Anonymous Services: Zero-knowledge proofs, anonymous portfolio management
- Trading-as-a-Service: Multi-exchange connectivity, risk management  
- Banking-as-a-Service: Payment processing, account management, compliance
"""

from .client import GridWorksSDK
from .config import GridWorksConfig, SDKOptions
from .exceptions import (
    GridWorksError,
    APIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    TimeoutError
)

# Service clients
from .ai_suite import AISuiteClient
from .anonymous_services import AnonymousServicesClient
from .trading import TradingClient
from .banking import BankingClient

# Type models
from .models.ai_suite import *
from .models.anonymous_services import *
from .models.trading import *
from .models.banking import *
from .models.common import *

__version__ = "1.0.0"
__author__ = "GridWorks Infrastructure Services"
__email__ = "sdk@gridworks.com"
__url__ = "https://github.com/raosunjoy/gridworks-infra"

__all__ = [
    # Main SDK
    "GridWorksSDK",
    "GridWorksConfig", 
    "SDKOptions",
    
    # Service clients
    "AISuiteClient",
    "AnonymousServicesClient", 
    "TradingClient",
    "BankingClient",
    
    # Exceptions
    "GridWorksError",
    "APIError",
    "AuthenticationError",
    "ValidationError", 
    "RateLimitError",
    "NetworkError",
    "TimeoutError",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__url__"
]