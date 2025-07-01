# GridWorks B2B Infrastructure Services REST API

## Overview

The GridWorks REST API provides complete access to all B2B infrastructure services through standard HTTP endpoints. This API enables integration with any programming language or platform that supports HTTP requests.

## Base URLs

- **Production**: `https://api.gridworks.com`
- **Staging**: `https://api-staging.gridworks.com`
- **Development**: `https://api-dev.gridworks.com`

## Authentication

All API requests require authentication using one of the following methods:

### API Key Authentication
Include your API key in the request header:
```http
X-API-Key: gw_prod_your_api_key_here
```

### JWT Token Authentication
Include a valid JWT token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Quick Start Examples

### cURL Examples

#### Get Client Information
```bash
curl -X GET "https://api.gridworks.com/api/v1/client/info" \
  -H "X-API-Key: gw_prod_your_api_key_here" \
  -H "Content-Type: application/json"
```

#### AI Support Request
```bash
curl -X POST "https://api.gridworks.com/api/v1/ai-suite/support" \
  -H "X-API-Key: gw_prod_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help with my portfolio analysis",
    "language": "en",
    "priority": "high"
  }'
```

#### Place Trading Order
```bash
curl -X POST "https://api.gridworks.com/api/v1/trading/orders" \
  -H "X-API-Key: gw_prod_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "side": "buy",
    "quantity": 100,
    "orderType": "limit",
    "price": 2450.50,
    "exchange": "NSE"
  }'
```

#### Process Payment
```bash
curl -X POST "https://api.gridworks.com/api/v1/banking/payments" \
  -H "X-API-Key: gw_prod_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000000,
    "currency": "INR",
    "fromAccount": "acc_sender_123",
    "toAccount": "acc_receiver_456",
    "paymentMethod": "bank_transfer",
    "purpose": "Investment transfer"
  }'
```

### JavaScript/Node.js Examples

#### Using Fetch API
```javascript
const apiKey = 'gw_prod_your_api_key_here';
const baseURL = 'https://api.gridworks.com';

// AI Support Request
async function getAISupport(message, language = 'en') {
  const response = await fetch(`${baseURL}/api/v1/ai-suite/support`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      language,
      priority: 'medium'
    })
  });
  
  return await response.json();
}

// Market Intelligence
async function getMorningPulse() {
  const response = await fetch(`${baseURL}/api/v1/ai-suite/intelligence`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'morning_pulse',
      parameters: {
        markets: ['NSE', 'BSE', 'NASDAQ'],
        analysisDepth: 'comprehensive'
      },
      deliveryFormat: 'text'
    })
  });
  
  return await response.json();
}

// Anonymous Portfolio Verification
async function verifyAnonymousPortfolio(portfolioData) {
  const response = await fetch(`${baseURL}/api/v1/anonymous/portfolio/verify`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      portfolioData: {
        totalValue: 50000000,
        assetClasses: [
          { type: 'equity', allocation: 60, performance: 12.5 },
          { type: 'bonds', allocation: 30, performance: 8.2 },
          { type: 'alternatives', allocation: 10, performance: 15.0 }
        ],
        riskProfile: 'moderate',
        timeHorizon: '5-10 years'
      },
      privacyLevel: 'obsidian'
    })
  });
  
  return await response.json();
}

// Trading Order
async function placeOrder(orderData) {
  const response = await fetch(`${baseURL}/api/v1/trading/orders`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });
  
  return await response.json();
}

// Usage examples
(async () => {
  try {
    // Get AI support
    const support = await getAISupport('Portfolio analysis needed', 'en');
    console.log('Support Response:', support.data.response);
    
    // Get morning pulse
    const pulse = await getMorningPulse();
    console.log('Morning Pulse:', pulse.data.analysis.summary);
    
    // Verify portfolio anonymously
    const verification = await verifyAnonymousPortfolio();
    console.log('Anonymous ID:', verification.data.anonymousId);
    
    // Place trading order
    const order = await placeOrder({
      symbol: 'RELIANCE',
      side: 'buy',
      quantity: 100,
      orderType: 'market'
    });
    console.log('Order ID:', order.data.orderId);
    
  } catch (error) {
    console.error('API Error:', error);
  }
})();
```

### Python Examples

#### Using Requests Library
```python
import requests
import json

API_KEY = 'gw_prod_your_api_key_here'
BASE_URL = 'https://api.gridworks.com'

headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

# AI Support Request
def get_ai_support(message, language='en'):
    url = f'{BASE_URL}/api/v1/ai-suite/support'
    data = {
        'message': message,
        'language': language,
        'priority': 'medium'
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# WhatsApp Support
def get_whatsapp_support(message, phone_number):
    url = f'{BASE_URL}/api/v1/ai-suite/support/whatsapp'
    data = {
        'message': message,
        'phoneNumber': phone_number
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Market Intelligence
def get_market_correlation(source_market, target_markets):
    url = f'{BASE_URL}/api/v1/ai-suite/intelligence'
    data = {
        'type': 'market_correlation',
        'parameters': {
            'markets': [source_market] + target_markets,
            'timeframe': '1M',
            'analysisDepth': 'detailed'
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Anonymous Portfolio Verification
def verify_anonymous_portfolio():
    url = f'{BASE_URL}/api/v1/anonymous/portfolio/verify'
    data = {
        'portfolioData': {
            'totalValue': 50000000,
            'assetClasses': [
                {'type': 'equity', 'allocation': 60, 'performance': 12.5},
                {'type': 'bonds', 'allocation': 30, 'performance': 8.2},
                {'type': 'alternatives', 'allocation': 10, 'performance': 15.0}
            ],
            'riskProfile': 'moderate',
            'timeHorizon': '5-10 years'
        },
        'privacyLevel': 'obsidian'
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Trading Order
def place_order(symbol, side, quantity, order_type='market', price=None):
    url = f'{BASE_URL}/api/v1/trading/orders'
    data = {
        'symbol': symbol,
        'side': side,
        'quantity': quantity,
        'orderType': order_type
    }
    if price:
        data['price'] = price
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Get Order Status
def get_order(order_id):
    url = f'{BASE_URL}/api/v1/trading/orders/{order_id}'
    response = requests.get(url, headers=headers)
    return response.json()

# Banking Payment
def process_payment(amount, currency, from_account, to_account, purpose):
    url = f'{BASE_URL}/api/v1/banking/payments'
    data = {
        'amount': amount,
        'currency': currency,
        'fromAccount': from_account,
        'toAccount': to_account,
        'paymentMethod': 'bank_transfer',
        'purpose': purpose
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Usage examples
if __name__ == '__main__':
    try:
        # Get AI support in Hindi
        support = get_ai_support('मुझे अपने पोर्टफोलियो के बारे में सहायता चाहिए', 'hi')
        print('Support Response:', support['data']['response'])
        
        # Get market correlation
        correlation = get_market_correlation('NASDAQ', ['NSE', 'BSE'])
        print('Correlation Analysis:', correlation['data']['analysis']['summary'])
        
        # Verify portfolio anonymously
        verification = verify_anonymous_portfolio()
        print('Anonymous ID:', verification['data']['anonymousId'])
        
        # Place trading order
        order = place_order('RELIANCE', 'buy', 100, 'limit', 2450.50)
        print('Order ID:', order['data']['orderId'])
        
        # Process payment
        payment = process_payment(1000000, 'INR', 'acc_123', 'acc_456', 'Investment')
        print('Payment ID:', payment['data']['paymentId'])
        
    except Exception as e:
        print(f'Error: {e}')
```

### Java Examples

#### Using OkHttp
```java
import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;

public class GridWorksAPIClient {
    private static final String API_KEY = "gw_prod_your_api_key_here";
    private static final String BASE_URL = "https://api.gridworks.com";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    
    private OkHttpClient client = new OkHttpClient();
    private Gson gson = new Gson();
    
    public String getAISupport(String message, String language) throws IOException {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("message", message);
        requestBody.addProperty("language", language);
        requestBody.addProperty("priority", "medium");
        
        RequestBody body = RequestBody.create(gson.toJson(requestBody), JSON);
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/v1/ai-suite/support")
            .header("X-API-Key", API_KEY)
            .post(body)
            .build();
            
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
    
    public String placeOrder(String symbol, String side, double quantity, 
                           String orderType, Double price) throws IOException {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("symbol", symbol);
        requestBody.addProperty("side", side);
        requestBody.addProperty("quantity", quantity);
        requestBody.addProperty("orderType", orderType);
        if (price != null) {
            requestBody.addProperty("price", price);
        }
        
        RequestBody body = RequestBody.create(gson.toJson(requestBody), JSON);
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/v1/trading/orders")
            .header("X-API-Key", API_KEY)
            .post(body)
            .build();
            
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
    
    public static void main(String[] args) {
        GridWorksAPIClient client = new GridWorksAPIClient();
        
        try {
            // Get AI support
            String supportResponse = client.getAISupport("Portfolio help needed", "en");
            System.out.println("Support: " + supportResponse);
            
            // Place order
            String orderResponse = client.placeOrder("RELIANCE", "buy", 100, "market", null);
            System.out.println("Order: " + orderResponse);
            
        } catch (IOException e) {
            System.err.println("API Error: " + e.getMessage());
        }
    }
}
```

## Service Endpoints

### AI Suite Services

#### Multi-language Support
- **POST** `/api/v1/ai-suite/support` - Get AI support response
- **POST** `/api/v1/ai-suite/support/whatsapp` - WhatsApp Business support
- **POST** `/api/v1/ai-suite/whatsapp/send` - Send WhatsApp message

#### Market Intelligence  
- **POST** `/api/v1/ai-suite/intelligence` - Get market analysis
- **GET** `/api/v1/ai-suite/analytics` - Usage analytics

#### Content Moderation
- **POST** `/api/v1/ai-suite/moderation` - Moderate content
- **GET** `/api/v1/ai-suite/experts/{expertId}/verify` - Verify expert

### Anonymous Services

#### Zero-Knowledge Proofs
- **POST** `/api/v1/anonymous/zk-proof/generate` - Generate ZK proof
- **POST** `/api/v1/anonymous/zk-proof/verify` - Verify ZK proof

#### Anonymous Portfolio Management
- **POST** `/api/v1/anonymous/portfolio/verify` - Verify portfolio anonymously
- **PUT** `/api/v1/anonymous/portfolio/{anonymousId}` - Update portfolio

#### Butler AI
- **POST** `/api/v1/anonymous/butler/assist` - Request Butler assistance

#### Deal Flow Sharing
- **POST** `/api/v1/anonymous/deals/share` - Share deal anonymously
- **GET** `/api/v1/anonymous/deals/available` - Get available deals

### Trading Services

#### Order Management
- **POST** `/api/v1/trading/orders` - Place order
- **GET** `/api/v1/trading/orders` - Get order history
- **GET** `/api/v1/trading/orders/{orderId}` - Get order details
- **DELETE** `/api/v1/trading/orders/{orderId}` - Cancel order

#### Market Data
- **GET** `/api/v1/trading/quote/{symbol}` - Get real-time quote
- **GET** `/api/v1/trading/candles/{symbol}` - Get price candles
- **GET** `/api/v1/trading/orderbook/{symbol}` - Get order book

#### Risk Management
- **POST** `/api/v1/trading/risk/assess` - Assess portfolio risk
- **POST** `/api/v1/trading/risk/pre-trade` - Pre-trade risk check

### Banking Services

#### Payment Processing
- **POST** `/api/v1/banking/payments` - Process payment
- **GET** `/api/v1/banking/payments/{paymentId}` - Get payment status
- **POST** `/api/v1/banking/payments/{paymentId}/cancel` - Cancel payment

#### Account Management
- **POST** `/api/v1/banking/accounts` - Create account
- **GET** `/api/v1/banking/accounts/{accountId}` - Get account details
- **GET** `/api/v1/banking/accounts/{accountId}/balance` - Get balance

#### Escrow Services
- **POST** `/api/v1/banking/escrow` - Create escrow
- **POST** `/api/v1/banking/escrow/{escrowId}/fund` - Fund escrow
- **POST** `/api/v1/banking/escrow/{escrowId}/release` - Release funds

#### Compliance
- **POST** `/api/v1/banking/compliance/kyc` - Perform KYC
- **POST** `/api/v1/banking/compliance/aml` - AML screening
- **GET** `/api/v1/banking/compliance/status/{clientId}` - Compliance status

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {
    // Response data specific to endpoint
  },
  "message": "Request completed successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "requestId": "gw_1234567890_abcdef"
}
```

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "fieldName",
    "reason": "Validation failed"
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "requestId": "gw_1234567890_abcdef"
}
```

## Rate Limiting

Rate limits vary by service tier:

| Tier | Requests/Hour | Burst Limit |
|------|---------------|-------------|
| Starter | 1,000 | 100/minute |
| Professional | 10,000 | 500/minute |
| Enterprise | 100,000 | 2,000/minute |
| Custom | Negotiated | Negotiated |

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9995
X-RateLimit-Reset: 1640995200
```

## Error Handling

### HTTP Status Codes

- **200** - Success
- **400** - Bad Request (validation error)
- **401** - Unauthorized (invalid credentials)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **429** - Too Many Requests (rate limit exceeded)
- **500** - Internal Server Error
- **503** - Service Unavailable

### Common Error Codes

- `INVALID_API_KEY` - API key is invalid or expired
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `VALIDATION_ERROR` - Request validation failed
- `INSUFFICIENT_BALANCE` - Insufficient account balance
- `ORDER_REJECTED` - Trading order rejected by risk engine
- `COMPLIANCE_REQUIRED` - KYC/AML compliance needed

## Webhooks

GridWorks supports webhooks for real-time notifications:

### Webhook Events

- `payment.completed` - Payment processing completed
- `payment.failed` - Payment processing failed
- `order.filled` - Trading order filled
- `order.cancelled` - Trading order cancelled
- `compliance.required` - Compliance action required
- `escrow.funded` - Escrow account funded
- `escrow.released` - Escrow funds released

### Webhook Payload Example

```json
{
  "event": "payment.completed",
  "data": {
    "paymentId": "pay_123456",
    "amount": 1000000,
    "currency": "INR",
    "status": "completed"
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "webhookId": "wh_abcdef123456"
}
```

## Testing

### Sandbox Environment

Use the development environment for testing:
- **Base URL**: `https://api-dev.gridworks.com`
- **API Key**: Use your development API key (`gw_dev_...`)

### Test Data

Development environment includes test data:
- Test trading symbols: `TEST_STOCK`, `TEST_BOND`
- Test accounts: `test_account_123`, `test_account_456`
- Test phone numbers: `+91TEST123456`

## SDKs and Tools

### Official SDKs
- **TypeScript/JavaScript**: `@gridworks/b2b-sdk`
- **Python**: `gridworks-b2b-sdk`

### API Tools
- **OpenAPI Specification**: Available at `/openapi.yaml`
- **Postman Collection**: Import from `/postman.json`
- **Insomnia Collection**: Import from `/insomnia.json`

## Support and Documentation

- **API Documentation**: [https://docs.gridworks.com/api](https://docs.gridworks.com/api)
- **Interactive API Explorer**: [https://api.gridworks.com/docs](https://api.gridworks.com/docs)
- **Support**: api-support@gridworks.com
- **Status Page**: [https://status.gridworks.com](https://status.gridworks.com)
- **GitHub**: [https://github.com/raosunjoy/gridworks-infra](https://github.com/raosunjoy/gridworks-infra)

---

**GridWorks B2B Infrastructure Services REST API - Complete financial infrastructure at your fingertips! 🚀**