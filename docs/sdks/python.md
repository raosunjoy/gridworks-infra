# Python SDK

## Enterprise-Grade Python SDK for GridWorks B2B Infrastructure

The GridWorks Python SDK provides a comprehensive, type-safe interface to all GridWorks B2B infrastructure services. Built with modern Python practices, it supports both synchronous and asynchronous operations, making it perfect for everything from simple scripts to high-performance applications.

---

## 🚀 Quick Start

### Installation

```bash
pip install gridworks-b2b-sdk
# or with async support
pip install gridworks-b2b-sdk[async]
```

### Basic Setup

```python
from gridworks_sdk import GridWorksSDK

# Synchronous client
client = GridWorksSDK(
    api_key="your-api-key",
    environment="production",  # or "sandbox"
    base_url="https://api.gridworks.com"
)

# Asynchronous client
async_client = GridWorksSDK(
    api_key="your-api-key",
    environment="production",
    async_mode=True
)
```

### First API Call

```python
# Synchronous
response = client.ai_suite.get_support_response(
    message="Hello, I need help with trading",
    language="en",
    context={
        "user_id": "user123",
        "session_id": "session456"
    }
)
print(response.reply)

# Asynchronous
async def main():
    response = await async_client.ai_suite.get_support_response(
        message="Hello, I need help with trading",
        language="hi",  # Hindi support
        context={
            "user_id": "user123",
            "session_id": "session456"
        }
    )
    print(response.reply)
```

---

## 🏗️ SDK Architecture

### Core Components

```python
from gridworks_sdk import GridWorksSDK
from gridworks_sdk.models import *
from gridworks_sdk.exceptions import *

class GridWorksSDK:
    """Main SDK client providing unified access to all services"""
    
    def __init__(self, config: GridWorksConfig):
        self.ai_suite = AISuiteClient(self)
        self.anonymous = AnonymousServicesClient(self)
        self.trading = TradingClient(self)
        self.banking = BankingClient(self)
        
        # Utility components
        self.config = config
        self.metrics = MetricsCollector()
        self.logger = Logger()
```

### Configuration

```python
from gridworks_sdk import GridWorksConfig, RetryConfig, LoggingConfig

config = GridWorksConfig(
    api_key="your-api-key",
    environment="production",
    base_url="https://api.gridworks.com",
    timeout=30.0,
    retry_config=RetryConfig(
        attempts=3,
        backoff_factor=2.0,
        max_delay=60.0,
        status_codes=[500, 502, 503, 504]
    ),
    logging_config=LoggingConfig(
        level="INFO",
        format="json",
        handlers=["console", "file"]
    )
)

client = GridWorksSDK(config)
```

---

## 🤖 AI Suite Client

### Support Engine

```python
from gridworks_sdk.models.ai import SupportRequest, SupportResponse

# Get AI Support Response
response = client.ai_suite.get_support_response(
    SupportRequest(
        message="How do I buy Reliance shares?",
        language="hi",  # Hindi
        context={
            "user_id": "user123",
            "conversation_id": "conv456",
            "platform": "whatsapp"
        }
    )
)

# Response handling
if response.confidence > 0.8:
    print(f"AI Response: {response.reply}")
    if response.suggested_actions:
        print("Suggested actions:")
        for action in response.suggested_actions:
            print(f"- {action.description}")
```

### Intelligence Engine

```python
from gridworks_sdk.models.ai import MorningPulseRequest, MarketIntelligenceRequest
from datetime import date

# Get Morning Pulse
morning_pulse = client.ai_suite.get_morning_pulse(
    MorningPulseRequest(
        date=date.today(),
        markets=["NSE", "BSE"],
        sectors=["TECHNOLOGY", "BANKING", "PHARMA"]
    )
)

print(f"Market Outlook: {morning_pulse.market_outlook}")
print(f"Key Events: {morning_pulse.key_events}")

# Market Intelligence
intelligence = client.ai_suite.get_market_intelligence(
    MarketIntelligenceRequest(
        symbol="RELIANCE",
        timeframe="1D",
        analysis_types=["technical", "fundamental", "sentiment"]
    )
)

print(f"Recommendation: {intelligence.recommendation}")
print(f"Price Target: ₹{intelligence.price_targets[0].target}")
print(f"Confidence: {intelligence.confidence}%")
```

### Moderation Engine

```python
from gridworks_sdk.models.ai import ContentModerationRequest

# Content Moderation
moderation = client.ai_suite.moderate_content(
    ContentModerationRequest(
        content="Check out this amazing stock tip! Guaranteed 500% returns!",
        content_type="message",
        platform="whatsapp",
        user_id="user123"
    )
)

if not moderation.approved:
    print("Content flagged for:")
    for flag in moderation.flags:
        print(f"- {flag.type}: {flag.reason}")
```

### WhatsApp Integration

```python
from gridworks_sdk.models.whatsapp import WhatsAppMessage, MessageTemplate

# Send WhatsApp Message
message = client.ai_suite.send_whatsapp_message(
    WhatsAppMessage(
        to="+919876543210",
        message_type="text",
        content="Your trading order has been executed successfully.",
        template=MessageTemplate(
            name="order_confirmation",
            parameters=["RELIANCE", "100", "₹2,500"]
        )
    )
)

# Handle WhatsApp Webhooks
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook/whatsapp", methods=["POST"])
def handle_whatsapp_webhook():
    webhook_data = request.json
    
    # Process incoming message
    response = client.ai_suite.process_whatsapp_message(webhook_data)
    
    # Send automated response
    if response.should_reply:
        client.ai_suite.send_whatsapp_message(response.reply_message)
    
    return {"status": "processed"}
```

---

## 🛡️ Anonymous Services Client

### Zero-Knowledge Portfolio Management

```python
from gridworks_sdk.models.anonymous import (
    ZKProofRequest, 
    AnonymousPortfolio,
    ProofVerificationRequest
)

# Generate ZK Proof for Portfolio
proof_request = ZKProofRequest(
    portfolio_value=50_000_000,  # ₹5Cr
    asset_classes=["equity", "debt", "alternative", "crypto"],
    proof_type="net_worth",
    tier="obsidian",
    verification_parameters={
        "min_threshold": 10_000_000,
        "max_threshold": 100_000_000,
        "currency": "INR"
    }
)

zk_proof = client.anonymous.generate_portfolio_proof(proof_request)

print(f"Proof generated for tier: {zk_proof.metadata.tier}")
print(f"Valid until: {zk_proof.metadata.expiry_date}")

# Verify ZK Proof
verification = client.anonymous.verify_portfolio_proof(
    ProofVerificationRequest(
        proof=zk_proof.proof,
        public_inputs=zk_proof.public_inputs,
        verification_key=zk_proof.verification_key
    )
)

if verification.is_valid:
    print(f"Portfolio verified for tier: {verification.tier}")
```

### Anonymous Communications

```python
from gridworks_sdk.models.anonymous import (
    AnonymousMessage,
    AnonymousIdentity,
    DealFlowShare
)

# Create Anonymous Identity
anon_identity = client.anonymous.create_anonymous_identity(
    AnonymousIdentity(
        tier="void",
        preferences={
            "deal_size_min": 100_000_000,
            "deal_size_max": 1_000_000_000,
            "sectors": ["fintech", "healthcare", "ai", "blockchain"],
            "geography": ["india", "singapore", "dubai", "cayman"],
            "investment_style": "growth",
            "check_size": "lead"
        },
        anonymity_level="maximum"
    )
)

# Send Anonymous Message
message = client.anonymous.send_anonymous_message(
    AnonymousMessage(
        recipient_id="anon_xyz789",
        message_type="deal_flow",
        content={
            "type": "investment_opportunity",
            "sector": "fintech",
            "stage": "series_b",
            "deal_size": 150_000_000,
            "description": "AI-powered trading platform seeking strategic investor",
            "timeline": "Q2_2025"
        },
        encryption_level="end_to_end",
        anonymous_id=anon_identity.anonymous_id
    )
)

# Share Deal Flow Anonymously
deal_share = client.anonymous.share_deal_flow(
    DealFlowShare(
        deal_id="deal_123",
        target_network="uhnw_investors",
        deal_summary={
            "sector": "fintech",
            "stage": "series_b",
            "valuation_range": "₹500Cr - ₹750Cr",
            "funding_required": "₹150Cr",
            "use_of_funds": ["product_development", "market_expansion", "team_scaling"]
        },
        matching_criteria={
            "min_check_size": 25_000_000,
            "sector_experience": True,
            "geographic_focus": ["india", "sea"]
        }
    )
)
```

### Butler AI

```python
from gridworks_sdk.models.anonymous import ButlerRequest, ButlerPersonality

# Interact with Butler AI
butler_response = client.anonymous.chat_with_butler(
    ButlerRequest(
        personality=ButlerPersonality.NEXUS,  # Sterling, Prism, or Nexus
        message="Find me private equity opportunities in Indian fintech with ticket sizes above ₹50Cr",
        context={
            "anonymous_id": anon_identity.anonymous_id,
            "tier": "void",
            "investment_focus": ["fintech", "b2b_saas"],
            "preferred_stage": ["series_b", "series_c"]
        },
        confidentiality_level="maximum"
    )
)

print(f"Butler Response: {butler_response.reply}")

if butler_response.investment_opportunities:
    print("\nInvestment Opportunities:")
    for opportunity in butler_response.investment_opportunities:
        print(f"- {opportunity.company_profile}")
        print(f"  Stage: {opportunity.funding_stage}")
        print(f"  Size: ₹{opportunity.deal_size:,}")

if butler_response.network_introductions:
    print("\nNetwork Introductions Available:")
    for intro in butler_response.network_introductions:
        print(f"- {intro.profile_summary}")
```

---

## 📈 Trading Client

### Order Management

```python
from gridworks_sdk.models.trading import (
    OrderRequest,
    OrderType,
    OrderSide,
    ProductType
)

# Place Order
order = client.trading.place_order(
    OrderRequest(
        symbol="RELIANCE",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.LIMIT,
        price=2500.50,
        exchange="NSE",
        product_type=ProductType.MIS,
        validity="DAY",
        disclosed_quantity=0,
        trigger_price=None
    )
)

print(f"Order placed: {order.order_id}")
print(f"Status: {order.status}")

# Get Order Status
order_status = client.trading.get_order_status(order.order_id)
print(f"Current status: {order_status.status}")

# Modify Order
modified_order = client.trading.modify_order(
    order.order_id,
    price=2550.00,
    quantity=150
)

# Cancel Order
cancellation = client.trading.cancel_order(order.order_id)
print(f"Cancellation status: {cancellation.status}")
```

### Portfolio Management

```python
from gridworks_sdk.models.trading import PortfolioMetricsRequest
from datetime import datetime, timedelta

# Get Portfolio
portfolio = client.trading.get_portfolio()
print(f"Total Value: ₹{portfolio.total_value:,.2f}")
print(f"Day P&L: ₹{portfolio.day_pnl:,.2f}")
print(f"Total P&L: ₹{portfolio.total_pnl:,.2f}")

# Get Positions
positions = client.trading.get_positions()
for position in positions:
    print(f"{position.symbol}: {position.quantity} @ ₹{position.average_price}")

# Get Portfolio Metrics
metrics = client.trading.get_portfolio_metrics(
    PortfolioMetricsRequest(
        period="1Y",
        benchmark="NIFTY50",
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now()
    )
)

print(f"Annual Return: {metrics.returns.yearly:.2%}")
print(f"Sharpe Ratio: {metrics.risk.sharpe_ratio:.2f}")
print(f"Max Drawdown: {metrics.risk.max_drawdown:.2%}")
print(f"Volatility: {metrics.risk.volatility:.2%}")
```

### Market Data

```python
from gridworks_sdk.models.trading import (
    QuoteRequest,
    HistoricalDataRequest,
    MarketDataSubscription
)

# Get Live Quotes
quotes = client.trading.get_quotes(["RELIANCE", "TCS", "INFY", "HDFCBANK"])
for quote in quotes:
    print(f"{quote.symbol}: ₹{quote.ltp} ({quote.change_percent:+.2f}%)")

# Get Historical Data
historical_data = client.trading.get_historical_data(
    HistoricalDataRequest(
        symbol="RELIANCE",
        interval="1D",
        from_date="2024-01-01",
        to_date="2024-12-31",
        exchange="NSE"
    )
)

# Process OHLCV data
for candle in historical_data.candles:
    print(f"{candle.timestamp}: O:{candle.open} H:{candle.high} L:{candle.low} C:{candle.close} V:{candle.volume}")

# Subscribe to Real-time Data (async)
async def subscribe_to_market_data():
    async for quote in client.trading.subscribe_to_quotes(["RELIANCE", "TCS"]):
        print(f"Real-time: {quote.symbol} = ₹{quote.ltp}")

# Using callbacks for real-time data
def on_quote_update(quote):
    print(f"Quote update: {quote.symbol} = ₹{quote.ltp}")

subscription = client.trading.subscribe_to_quotes(
    symbols=["RELIANCE", "TCS"],
    callback=on_quote_update
)
```

### Algorithmic Trading

```python
from gridworks_sdk.models.trading import (
    TradingStrategy,
    StrategyBacktest,
    StrategyDeployment
)

# Define Trading Strategy
strategy = TradingStrategy(
    name="Mean Reversion Strategy",
    description="Simple mean reversion based on RSI",
    parameters={
        "rsi_period": 14,
        "overbought_threshold": 70,
        "oversold_threshold": 30,
        "position_size": 0.1,  # 10% of portfolio
        "stop_loss": 0.05,     # 5% stop loss
        "take_profit": 0.1     # 10% take profit
    },
    symbols=["RELIANCE", "TCS", "INFY"],
    timeframe="15m"
)

# Backtest Strategy
backtest = client.trading.backtest_strategy(
    StrategyBacktest(
        strategy=strategy,
        start_date="2023-01-01",
        end_date="2024-01-01",
        initial_capital=1_000_000
    )
)

print(f"Backtest Results:")
print(f"Total Return: {backtest.total_return:.2%}")
print(f"Sharpe Ratio: {backtest.sharpe_ratio:.2f}")
print(f"Max Drawdown: {backtest.max_drawdown:.2%}")

# Deploy Strategy (if backtest is satisfactory)
if backtest.sharpe_ratio > 1.5:
    deployment = client.trading.deploy_strategy(
        StrategyDeployment(
            strategy=strategy,
            capital_allocation=500_000,
            risk_limits={
                "max_position_size": 100_000,
                "max_daily_loss": 25_000,
                "max_leverage": 2.0
            }
        )
    )
    print(f"Strategy deployed: {deployment.deployment_id}")
```

---

## 💳 Banking Client

### Payment Processing

```python
from gridworks_sdk.models.banking import (
    PaymentRequest,
    PaymentMethod,
    PaymentPurpose
)

# Process Payment
payment = client.banking.process_payment(
    PaymentRequest(
        amount=100_000.00,
        currency="INR",
        from_account="acc_123456",
        to_account="acc_789012",
        payment_method=PaymentMethod.UPI,
        purpose=PaymentPurpose.TRADING_DEPOSIT,
        reference="TXN_001",
        description="Deposit for trading account",
        metadata={
            "client_id": "client_123",
            "transaction_type": "deposit"
        }
    )
)

print(f"Payment initiated: {payment.transaction_id}")
print(f"Status: {payment.status}")

# Get Payment Status
payment_status = client.banking.get_payment_status(payment.transaction_id)
print(f"Current status: {payment_status.status}")

# Process Bulk Payments
bulk_payments = client.banking.process_bulk_payments([
    PaymentRequest(
        amount=50_000,
        currency="INR",
        from_account="acc_123456",
        to_account="acc_111111",
        payment_method=PaymentMethod.NEFT,
        purpose=PaymentPurpose.SETTLEMENT,
        reference="BULK_001_1"
    ),
    PaymentRequest(
        amount=75_000,
        currency="INR",
        from_account="acc_123456", 
        to_account="acc_222222",
        payment_method=PaymentMethod.RTGS,
        purpose=PaymentPurpose.SETTLEMENT,
        reference="BULK_001_2"
    )
])

print(f"Bulk payment batch: {bulk_payments.batch_id}")
```

### Account Management

```python
from gridworks_sdk.models.banking import (
    VirtualAccountRequest,
    AccountType,
    TransactionHistoryRequest
)

# Create Virtual Account
virtual_account = client.banking.create_virtual_account(
    VirtualAccountRequest(
        account_type=AccountType.TRADING,
        currency="INR",
        client_id="client_123",
        account_name="Trading Account - HDFC",
        features=["UPI", "NEFT", "RTGS", "IMPS"],
        limits={
            "daily_transaction_limit": 1_000_000,
            "monthly_transaction_limit": 10_000_000,
            "per_transaction_limit": 500_000
        }
    )
)

print(f"Virtual account created: {virtual_account.account_number}")
print(f"IFSC Code: {virtual_account.ifsc_code}")

# Get Account Balance
balance = client.banking.get_account_balance("acc_123456")
print(f"Available Balance: ₹{balance.available_balance:,.2f}")
print(f"Ledger Balance: ₹{balance.ledger_balance:,.2f}")

# Get Transaction History
transactions = client.banking.get_transaction_history(
    TransactionHistoryRequest(
        account_id="acc_123456",
        from_date="2024-01-01",
        to_date="2024-12-31",
        transaction_types=["CREDIT", "DEBIT"],
        limit=100,
        offset=0
    )
)

for txn in transactions.transactions:
    print(f"{txn.date}: {txn.type} ₹{txn.amount} - {txn.description}")
```

### KYC/AML Compliance

```python
from gridworks_sdk.models.banking import (
    KYCRequest,
    AMLCheckRequest,
    DocumentVerification,
    ComplianceStatus
)

# Initiate KYC Process
kyc_documents = [
    DocumentVerification(
        document_type="PAN",
        document_number="ABCDE1234F",
        file_url="https://storage.gridworks.com/docs/pan_123.pdf",
        verification_required=True
    ),
    DocumentVerification(
        document_type="AADHAAR",
        document_number="1234-5678-9012",
        file_url="https://storage.gridworks.com/docs/aadhaar_123.pdf",
        verification_required=True
    ),
    DocumentVerification(
        document_type="BANK_STATEMENT",
        file_url="https://storage.gridworks.com/docs/statement_123.pdf",
        verification_required=False
    )
]

kyc_process = client.banking.initiate_kyc(
    KYCRequest(
        customer_id="cust_123",
        documents=kyc_documents,
        verification_method="AUTOMATED",
        priority="HIGH"
    )
)

print(f"KYC Process ID: {kyc_process.process_id}")
print(f"Estimated completion: {kyc_process.estimated_completion}")

# Check AML Status
aml_check = client.banking.perform_aml_check(
    AMLCheckRequest(
        customer_id="cust_123",
        transaction_id="txn_456",
        check_types=["SANCTIONS", "PEP", "ADVERSE_MEDIA"],
        risk_level="HIGH"
    )
)

if aml_check.risk_score > 75:
    print(f"High risk transaction detected: {aml_check.risk_factors}")
    # Trigger manual review
    review = client.banking.trigger_manual_review(aml_check.check_id)
```

### Escrow Services

```python
from gridworks_sdk.models.banking import (
    EscrowRequest,
    EscrowCondition,
    EscrowRelease
)

# Create Escrow
escrow_conditions = [
    EscrowCondition(
        condition_type="DOCUMENT_VERIFICATION",
        description="Completion of due diligence documents",
        required_parties=["buyer", "seller"],
        verification_method="MANUAL"
    ),
    EscrowCondition(
        condition_type="REGULATORY_APPROVAL",
        description="SEBI approval for transaction",
        required_parties=["regulator"],
        verification_method="AUTOMATED"
    )
]

escrow = client.banking.create_escrow(
    EscrowRequest(
        amount=10_000_000,  # ₹1Cr
        currency="INR",
        parties={
            "buyer": "party_buyer_123",
            "seller": "party_seller_456",
            "escrow_agent": "gridworks_escrow"
        },
        conditions=escrow_conditions,
        release_schedule="CONDITIONAL",
        expiry_date="2025-06-30",
        fees={
            "escrow_fee": 0.005,  # 0.5%
            "fee_payer": "buyer"
        }
    )
)

print(f"Escrow created: {escrow.escrow_id}")

# Release Escrow (when conditions are met)
escrow_release = client.banking.release_escrow(
    EscrowRelease(
        escrow_id=escrow.escrow_id,
        release_amount=10_000_000,
        release_to="party_seller_456",
        conditions_verified=[
            {"condition_id": "cond_1", "verified_by": "manual_reviewer", "status": "VERIFIED"},
            {"condition_id": "cond_2", "verified_by": "automated_system", "status": "VERIFIED"}
        ]
    )
)
```

---

## 🔄 Asynchronous Operations

### Async Client Usage

```python
import asyncio
from gridworks_sdk import AsyncGridWorksSDK

async def main():
    # Create async client
    async_client = AsyncGridWorksSDK(
        api_key="your-api-key",
        environment="production"
    )
    
    # Multiple concurrent operations
    tasks = [
        async_client.trading.get_portfolio(),
        async_client.banking.get_account_balance("acc_123"),
        async_client.ai_suite.get_morning_pulse(),
        async_client.anonymous.get_portfolio_analytics()
    ]
    
    # Execute concurrently
    portfolio, balance, pulse, analytics = await asyncio.gather(*tasks)
    
    print(f"Portfolio Value: ₹{portfolio.total_value:,.2f}")
    print(f"Account Balance: ₹{balance.available_balance:,.2f}")
    print(f"Market Outlook: {pulse.market_outlook}")
    print(f"Anonymous Holdings: {analytics.total_verified_holdings}")
    
    # Close client
    await async_client.close()

# Run async operations
asyncio.run(main())
```

### Async Context Manager

```python
async def trading_operations():
    async with AsyncGridWorksSDK(api_key="your-api-key") as client:
        # Place multiple orders concurrently
        order_tasks = [
            client.trading.place_order(OrderRequest(
                symbol="RELIANCE",
                side=OrderSide.BUY,
                quantity=100,
                order_type=OrderType.MARKET
            )),
            client.trading.place_order(OrderRequest(
                symbol="TCS",
                side=OrderSide.BUY,
                quantity=50,
                order_type=OrderType.MARKET
            ))
        ]
        
        orders = await asyncio.gather(*order_tasks)
        
        for order in orders:
            print(f"Order {order.order_id} placed for {order.symbol}")
```

### Streaming Data

```python
async def stream_market_data():
    async with AsyncGridWorksSDK(api_key="your-api-key") as client:
        # Stream real-time quotes
        async for quote in client.trading.stream_quotes(["RELIANCE", "TCS", "INFY"]):
            print(f"{quote.symbol}: ₹{quote.ltp} @ {quote.timestamp}")
            
            # Place order based on price movement
            if quote.change_percent > 2.0:
                order = await client.trading.place_order(
                    OrderRequest(
                        symbol=quote.symbol,
                        side=OrderSide.BUY,
                        quantity=10,
                        order_type=OrderType.MARKET
                    )
                )
                print(f"Momentum order placed: {order.order_id}")

asyncio.run(stream_market_data())
```

---

## 🛠️ Advanced Features

### Custom Request Headers

```python
client = GridWorksSDK(
    api_key="your-api-key",
    environment="production",
    default_headers={
        "X-Client-Version": "1.0.0",
        "X-Request-Source": "python-sdk",
        "X-Trace-ID": "custom-trace-123"
    }
)
```

### Request Interceptors

```python
def request_interceptor(request):
    """Add custom logic before request is sent"""
    request.headers["X-Request-Time"] = str(time.time())
    request.headers["X-Client-IP"] = get_client_ip()
    return request

def response_interceptor(response):
    """Process response before returning to caller"""
    log_api_response(response)
    return response

client.add_request_interceptor(request_interceptor)
client.add_response_interceptor(response_interceptor)
```

### Error Handling

```python
from gridworks_sdk.exceptions import (
    GridWorksAPIError,
    GridWorksNetworkError,
    GridWorksAuthenticationError,
    GridWorksRateLimitError,
    GridWorksValidationError
)

try:
    order = client.trading.place_order(order_request)
except GridWorksAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Refresh API key or re-authenticate
except GridWorksRateLimitError as e:
    print(f"Rate limit exceeded: {e.retry_after} seconds")
    # Wait and retry
    time.sleep(e.retry_after)
except GridWorksValidationError as e:
    print(f"Invalid request data: {e.validation_errors}")
    # Fix request data
except GridWorksAPIError as e:
    print(f"API error: {e.error_code} - {e.message}")
    # Handle specific error codes
    if e.error_code == "INSUFFICIENT_FUNDS":
        # Handle insufficient funds
        pass
except GridWorksNetworkError as e:
    print(f"Network error: {e.message}")
    # Retry with exponential backoff
```

### Metrics and Monitoring

```python
# Get SDK metrics
metrics = client.get_metrics()
print(f"Total API calls: {metrics.total_calls}")
print(f"Success rate: {metrics.success_rate:.2%}")
print(f"Average response time: {metrics.avg_response_time:.2f}ms")

# Custom metrics
client.metrics.increment("custom.orders.placed")
client.metrics.gauge("custom.portfolio.value", portfolio_value)
client.metrics.histogram("custom.order.execution_time", execution_time)

# Export metrics to monitoring system
prometheus_metrics = client.metrics.to_prometheus()
```

---

## 🧪 Testing and Development

### Mock Client for Testing

```python
from gridworks_sdk.testing import MockGridWorksSDK
import unittest

class TestTradingOperations(unittest.TestCase):
    def setUp(self):
        self.mock_client = MockGridWorksSDK()
        
        # Configure mock responses
        self.mock_client.trading.place_order.return_value = Order(
            order_id="mock_123",
            status="SUBMITTED",
            symbol="RELIANCE",
            side="BUY",
            quantity=100
        )
    
    def test_place_order(self):
        order = self.mock_client.trading.place_order(
            OrderRequest(
                symbol="RELIANCE",
                side=OrderSide.BUY,
                quantity=100,
                order_type=OrderType.MARKET
            )
        )
        
        self.assertEqual(order.order_id, "mock_123")
        self.assertEqual(order.status, "SUBMITTED")
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = GridWorksSDK(
    api_key="your-api-key",
    debug=True,  # Enable debug mode
    log_level="DEBUG"
)

# All API calls will be logged with request/response details
portfolio = client.trading.get_portfolio()
```

### Custom Serialization

```python
from gridworks_sdk.serializers import JSONSerializer, XMLSerializer

# Use custom serializer
client = GridWorksSDK(
    api_key="your-api-key",
    serializer=XMLSerializer()  # Default is JSONSerializer
)
```

---

## 🐍 Framework Integration

### Django Integration

```python
# settings.py
GRIDWORKS_CONFIG = {
    'API_KEY': 'your-api-key',
    'ENVIRONMENT': 'production',
    'BASE_URL': 'https://api.gridworks.com'
}

# views.py
from django.shortcuts import render
from django.http import JsonResponse
from gridworks_sdk import GridWorksSDK

def get_portfolio(request):
    client = GridWorksSDK(
        api_key=settings.GRIDWORKS_CONFIG['API_KEY'],
        environment=settings.GRIDWORKS_CONFIG['ENVIRONMENT']
    )
    
    portfolio = client.trading.get_portfolio()
    
    return JsonResponse({
        'total_value': portfolio.total_value,
        'day_pnl': portfolio.day_pnl,
        'positions': [p.dict() for p in portfolio.positions]
    })
```

### Flask Integration

```python
from flask import Flask, jsonify, request
from gridworks_sdk import GridWorksSDK

app = Flask(__name__)

# Initialize client
client = GridWorksSDK(
    api_key=os.environ['GRIDWORKS_API_KEY'],
    environment='production'
)

@app.route('/api/orders', methods=['POST'])
def place_order():
    try:
        order_data = request.json
        order = client.trading.place_order(
            OrderRequest(**order_data)
        )
        return jsonify(order.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio')
def get_portfolio():
    portfolio = client.trading.get_portfolio()
    return jsonify(portfolio.dict())
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from gridworks_sdk import GridWorksSDK
from gridworks_sdk.models.trading import OrderRequest

app = FastAPI()

client = GridWorksSDK(
    api_key="your-api-key",
    environment="production"
)

@app.post("/orders/")
async def place_order(order_request: OrderRequest):
    try:
        order = await client.trading.place_order(order_request)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/")
async def get_portfolio():
    portfolio = await client.trading.get_portfolio()
    return portfolio
```

---

## 📊 Data Models and Types

### Core Data Models

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"

class Order(BaseModel):
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: Optional[float]
    order_type: OrderType
    status: str
    timestamp: datetime
    
class Portfolio(BaseModel):
    total_value: float
    day_pnl: float
    total_pnl: float
    positions: List[Position]
    holdings: List[Holding]
    
class ZKProof(BaseModel):
    proof: str
    public_inputs: List[str]
    verification_key: str
    metadata: ProofMetadata
```

---

## 🚀 Performance Optimization

### Connection Pooling

```python
from gridworks_sdk import GridWorksSDK
import httpx

# Custom HTTP client with connection pooling
http_client = httpx.Client(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0
    ),
    timeout=30.0
)

client = GridWorksSDK(
    api_key="your-api-key",
    http_client=http_client
)
```

### Batch Operations

```python
# Batch multiple operations
async def batch_operations():
    batch = client.create_batch()
    
    # Add operations to batch
    batch.add('portfolio', client.trading.get_portfolio())
    batch.add('balance', client.banking.get_account_balance('acc_123'))
    batch.add('quotes', client.trading.get_quotes(['RELIANCE', 'TCS']))
    
    # Execute batch
    results = await batch.execute()
    
    portfolio = results['portfolio']
    balance = results['balance']
    quotes = results['quotes']
```

### Caching

```python
from gridworks_sdk.cache import RedisCache

# Configure caching
cache = RedisCache(
    host='localhost',
    port=6379,
    db=0,
    default_ttl=300  # 5 minutes
)

client = GridWorksSDK(
    api_key="your-api-key",
    cache=cache
)

# Subsequent calls will use cached results if available
portfolio1 = client.trading.get_portfolio()  # API call
portfolio2 = client.trading.get_portfolio()  # Cached result
```

---

The GridWorks Python SDK provides a comprehensive, type-safe, and high-performance interface to all GridWorks B2B infrastructure services, enabling rapid development of enterprise-grade financial applications in Python.