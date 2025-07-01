# GridWorks B2B Infrastructure Services Python SDK

## Overview

The GridWorks B2B Python SDK provides comprehensive access to all GridWorks infrastructure services for financial institutions. This SDK enables rapid integration with our enterprise-grade B2B services.

## Services Included

- **AI Suite**: Multi-language support, market intelligence, content moderation
- **Anonymous Services**: Zero-knowledge proofs, anonymous portfolio management (World's First)
- **Trading-as-a-Service**: Multi-exchange connectivity, risk management
- **Banking-as-a-Service**: Payment processing, account management, compliance

## Installation

```bash
pip install gridworks-b2b-sdk
```

## Quick Start

```python
from gridworks_sdk import GridWorksSDK, Environment

# Initialize SDK
sdk = GridWorksSDK.create_for_environment(
    Environment.PRODUCTION,  # or DEVELOPMENT, STAGING
    "gw_prod_your_api_key_here",
    "your_client_id"
)

# Test connectivity
is_healthy = sdk.health_check()
print(f"SDK Status: {is_healthy}")
```

## Configuration

```python
from gridworks_sdk import GridWorksSDK, GridWorksConfig, SDKOptions

# Detailed configuration
config = GridWorksConfig(
    api_key="gw_prod_your_api_key_here",
    client_id="your_client_id",
    environment="production",
    timeout=30.0,
    debug=False
)

options = SDKOptions(
    enable_logging=True,
    max_concurrent_requests=20
)

sdk = GridWorksSDK(config, options)
```

## Service Usage Examples

### AI Suite Services

#### Multi-language Support
```python
# Get support in Hindi
response = sdk.ai_suite.get_support(
    message="मुझे अपने पोर्टफोलियो के बारे में सहायता चाहिए",
    language="hi",
    priority="high"
)

# Get morning pulse
morning_pulse = sdk.ai_suite.get_morning_pulse(
    markets=["NSE", "BSE", "NASDAQ"],
    delivery_format="whatsapp"
)
```

#### WhatsApp Business Integration
```python
# Send WhatsApp support message
whatsapp_response = sdk.ai_suite.get_whatsapp_support(
    message="Portfolio analysis required",
    phone_number="+919876543210"
)

# Send WhatsApp message
send_result = sdk.ai_suite.send_whatsapp_message(
    to="+919876543210",
    content="Your investment update is ready",
    message_type="text"
)
```

### Anonymous Services (World's First)

#### Anonymous Portfolio Verification
```python
# Verify portfolio anonymously with ZK proofs
portfolio_verification = sdk.anonymous.verify_anonymous_portfolio(
    portfolio_data={
        "totalValue": 50000000,  # ₹5Cr
        "assetClasses": [
            {"type": "equity", "allocation": 60, "performance": 12.5},
            {"type": "bonds", "allocation": 30, "performance": 8.2},
            {"type": "alternatives", "allocation": 10, "performance": 15.0}
        ],
        "riskProfile": "moderate",
        "timeHorizon": "5-10 years"
    },
    privacy_level="obsidian"  # ₹2Cr-5Cr tier
)

print(f"Anonymous ID: {portfolio_verification.data['anonymousId']}")
```

#### Butler AI Assistance
```python
# Get investment advice from Butler AI
butler_advice = sdk.anonymous.request_butler_assistance(
    request="Investment advice for private equity with moderate risk tolerance",
    personality="sterling",
    context={
        "portfolioTier": "obsidian",
        "anonymousId": portfolio_verification.data["anonymousId"]
    }
)

print(f"Butler Response: {butler_advice.data['response']}")
```

#### Anonymous Deal Flow
```python
# Share deal anonymously
deal_share = sdk.anonymous.share_deal_flow({
    "dealId": "deal_123",
    "dealType": "private_equity",
    "minimumInvestment": 10000000,  # ₹1Cr
    "targetReturns": {
        "expected": 18,
        "minimum": 12,
        "timeframe": "3-5 years"
    },
    "anonymityRequirements": {
        "dealSourceAnonymous": True,
        "investorAnonymous": True,
        "intermediaryRequired": True
    }
})

# Get available deals
available_deals = sdk.anonymous.get_available_deals(
    anonymous_id=portfolio_verification.data["anonymousId"],
    filters={
        "dealType": "private_equity",
        "minimumInvestment": 5000000
    }
)
```

### Trading-as-a-Service

#### Order Management
```python
# Place buy order
order_response = sdk.trading.place_order(
    symbol="RELIANCE",
    side="buy",
    quantity=100,
    order_type="limit",
    price=2450.50,
    exchange="NSE"
)

print(f"Order ID: {order_response.data['orderId']}")

# Check order status
order_status = sdk.trading.get_order(order_response.data["orderId"])
print(f"Order Status: {order_status.data['status']}")
```

#### Market Data
```python
# Get real-time quote
quote = sdk.trading.get_quote("RELIANCE", exchange="NSE")
print(f"Current Price: {quote.data['data']['price']}")

# Get historical candles
candles = sdk.trading.get_candles(
    symbol="RELIANCE",
    interval="1d",
    start_time="2024-01-01",
    end_time="2024-01-31",
    limit=30
)

for candle in candles.data["candles"]:
    print(f"Date: {candle['timestamp']}, Close: {candle['close']}")
```

#### Risk Assessment
```python
# Pre-trade risk check
risk_check = sdk.trading.pre_trade_risk_check({
    "symbol": "RELIANCE",
    "side": "buy",
    "quantity": 1000,
    "orderType": "market"
})

if risk_check.data["approved"]:
    print("Trade approved")
else:
    print(f"Risk warnings: {risk_check.data['warnings']}")

# Portfolio risk assessment
portfolio_risk = sdk.trading.assess_risk(
    portfolio_id="portfolio_123",
    proposed_trade={
        "symbol": "RELIANCE",
        "side": "buy",
        "quantity": 1000
    }
)
```

### Banking-as-a-Service

#### Payment Processing
```python
# Process payment
payment = sdk.banking.process_payment(
    amount=1000000,  # ₹10L
    currency="INR",
    from_account="acc_sender_123",
    to_account="acc_receiver_456",
    payment_method="bank_transfer",
    purpose="Investment transfer"
)

print(f"Payment ID: {payment.data['paymentId']}")
print(f"Status: {payment.data['status']}")
```

#### Account Management
```python
# Create virtual account
account = sdk.banking.create_account(
    account_type="virtual",
    currency="INR",
    client_id="client_123",
    account_name="Trading Account",
    purpose="Securities trading"
)

print(f"Account ID: {account.data['accountId']}")
print(f"Account Number: {account.data['accountNumber']}")

# Get account balance
balance = sdk.banking.get_account_balance(account.data["accountId"])
print(f"Available Balance: {balance.data['balance']['available']}")
```

#### Escrow Services
```python
# Create escrow for large transaction
escrow = sdk.banking.create_escrow(
    amount=50000000,  # ₹5Cr
    currency="INR",
    parties={
        "buyer": {
            "accountId": "acc_buyer_123",
            "name": "Buyer Corp",
            "email": "buyer@corp.com"
        },
        "seller": {
            "accountId": "acc_seller_456", 
            "name": "Seller Ltd",
            "email": "seller@ltd.com"
        }
    },
    terms={
        "description": "Private equity investment",
        "conditions": ["due_diligence_complete", "legal_approval"],
        "disputeResolution": "arbitration",
        "timeoutAction": "refund"
    },
    timeline={
        "fundingDeadline": "2024-02-15T23:59:59Z",
        "completionDeadline": "2024-03-31T23:59:59Z",
        "inspectionPeriod": 30
    }
)

print(f"Escrow ID: {escrow.data['escrowId']}")
```

#### Compliance (KYC/AML)
```python
# Perform KYC
kyc_result = sdk.banking.perform_kyc(
    client_id="client_123",
    documents=[
        {
            "type": "passport",
            "file_data": "base64_encoded_file",
            "metadata": {"issueDate": "2020-01-15", "expiryDate": "2030-01-15"}
        },
        {
            "type": "address_proof", 
            "file_data": "base64_encoded_file"
        }
    ]
)

print(f"KYC Status: {kyc_result.data['status']}")

# Check compliance status
compliance = sdk.banking.get_compliance_status("client_123")
print(f"Overall Status: {compliance.data['overallStatus']}")
```

## Async/Await Support

```python
import asyncio
from gridworks_sdk import GridWorksSDK

async def main():
    sdk = GridWorksSDK.create_for_environment(
        "production",
        "your_api_key",
        "your_client_id"
    )
    
    # Async request
    response = await sdk.async_request(
        "GET", 
        "/api/v1/client/info"
    )
    
    print(f"Client Info: {response.data}")

# Run async function
asyncio.run(main())
```

## Error Handling

```python
from gridworks_sdk.exceptions import (
    APIError, 
    AuthenticationError, 
    RateLimitError,
    ValidationError
)

try:
    response = sdk.ai_suite.get_support(
        message="Help with portfolio",
        language="en"
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limit exceeded, retry after: {e.retry_after}")
except ValidationError as e:
    print(f"Validation error in field '{e.field}': {e.message}")
except APIError as e:
    print(f"API Error {e.status_code}: {e.message}")
```

## Context Manager Usage

```python
# Automatic resource cleanup
with GridWorksSDK.create_for_environment(
    "production", 
    "your_api_key", 
    "your_client_id"
) as sdk:
    
    response = sdk.ai_suite.get_support(
        message="Portfolio help needed",
        language="en"
    )
    
    print(response.data)
# SDK session automatically closed
```

## Request Metrics and Monitoring

```python
# Get request metrics
metrics = sdk.get_metrics()
for metric in metrics:
    print(f"Endpoint: {metric.endpoint}")
    print(f"Duration: {metric.duration}s")
    print(f"Status: {metric.status_code}")
    print("---")

# Clear metrics
sdk.clear_metrics()

# Service-specific analytics
ai_analytics = sdk.ai_suite.get_usage_analytics("30d")
trading_analytics = sdk.trading.get_portfolio_performance("portfolio_123", "1M")
banking_analytics = sdk.banking.get_compliance_status("client_123")
```

## Configuration Examples

### Development Environment
```python
# Development with debug logging
dev_sdk = GridWorksSDK.create_for_environment(
    Environment.DEVELOPMENT,
    "gw_dev_your_api_key",
    "dev_client_id"
)

# Configure options
options = SDKOptions(
    enable_logging=True,
    log_level="DEBUG",
    max_concurrent_requests=5,
    websocket=WebSocketConfig(
        auto_reconnect=True,
        reconnect_interval=3.0
    )
)

dev_sdk = GridWorksSDK(dev_config, options)
```

### Production Environment
```python
# Production with custom headers
prod_config = GridWorksConfig(
    api_key="gw_prod_your_api_key",
    client_id="prod_client_id", 
    environment=Environment.PRODUCTION,
    headers={
        "X-Custom-Header": "enterprise-client",
        "X-Request-Source": "trading-dashboard"
    },
    timeout=60.0
)

prod_sdk = GridWorksSDK(prod_config)
```

## Advanced Features

### Retry Configuration
```python
from gridworks_sdk.config import RetryConfig

config = GridWorksConfig(
    api_key="your_api_key",
    client_id="your_client_id", 
    environment="production",
    retry=RetryConfig(
        attempts=5,
        delay=2.0,
        backoff=1.5
    )
)
```

### Custom Request Headers
```python
# Add custom headers to all requests
sdk.update_config(headers={
    "X-Custom-Client": "trading-platform",
    "X-Version": "2.1.0"
})
```

### API Key Validation
```python
# Validate API key format
is_valid = GridWorksSDK.validate_api_key("gw_prod_...")
if not is_valid:
    print("Invalid API key format")
```

## Type Hints and IDE Support

The SDK includes comprehensive type hints for better IDE support:

```python
from typing import Dict, Any, Optional
from gridworks_sdk import GridWorksSDK, APIResponse

def process_trading_order(sdk: GridWorksSDK, 
                         order_data: Dict[str, Any]) -> Optional[str]:
    """
    Process trading order and return order ID
    
    Args:
        sdk: GridWorks SDK instance
        order_data: Order information
        
    Returns:
        Order ID if successful, None otherwise
    """
    try:
        response: APIResponse = sdk.trading.place_order(**order_data)
        if response.success:
            return response.data["orderId"]
    except Exception as e:
        print(f"Order failed: {e}")
    
    return None
```

## Rate Limiting

The SDK automatically handles rate limits with exponential backoff:

```python
# SDK will automatically retry with backoff
try:
    for i in range(100):
        response = sdk.ai_suite.get_support(f"Message {i}")
        print(f"Response {i}: Success")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.retry_after}s")
```

## Security Best Practices

1. **Environment Variables**:
   ```python
   import os
   
   config = GridWorksConfig(
       api_key=os.getenv("GRIDWORKS_API_KEY"),
       client_id=os.getenv("GRIDWORKS_CLIENT_ID"),
       environment=Environment.PRODUCTION
   )
   ```

2. **API Key Validation**:
   ```python
   api_key = os.getenv("GRIDWORKS_API_KEY")
   if not GridWorksSDK.validate_api_key(api_key):
       raise ValueError("Invalid API key format")
   ```

3. **Secure Configuration**:
   - Never hardcode API keys
   - Use environment variables or secure vaults
   - Validate all inputs before sending requests

## Testing

```python
# Mock SDK for testing
from unittest.mock import patch, MagicMock

with patch('gridworks_sdk.GridWorksSDK') as mock_sdk:
    mock_sdk.return_value.ai_suite.get_support.return_value = APIResponse(
        success=True,
        data={"response": "Test response"},
        timestamp="2024-01-01T00:00:00Z",
        request_id="test_123"
    )
    
    # Your test code here
```

## Documentation and Support

- **API Documentation**: [https://docs.gridworks.com/api](https://docs.gridworks.com/api)
- **Python SDK Docs**: [https://docs.gridworks.com/sdk/python](https://docs.gridworks.com/sdk/python)
- **Support**: support@gridworks.com
- **GitHub**: [https://github.com/raosunjoy/gridworks-infra](https://github.com/raosunjoy/gridworks-infra)

## License

MIT License - see LICENSE file for details.

---

**GridWorks B2B Infrastructure Services Python SDK - Powering the future of financial technology! 🚀**