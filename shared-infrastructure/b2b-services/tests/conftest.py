"""
GridWorks B2B Services - Test Configuration & Fixtures
Comprehensive test setup with 100% coverage requirements
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import redis
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import secrets
import json
from typing import Dict, Any, Generator, AsyncGenerator

from ..main import app
from ..database.models import Base, EnterpriseClient, User, APIKey, B2BService
from ..database.session import get_db
from ..config import settings
from ..auth.enterprise_auth import get_current_user, get_api_key_data
from ..ai_suite.support_engine import get_support_engine
from ..ai_suite.intelligence_engine import get_intelligence_engine
from ..ai_suite.moderator_engine import get_moderator_engine
from ..anonymous_services.zk_proof_system import get_zk_proof_system, get_anonymous_portfolio_manager


# Test database URL (SQLite in-memory for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test Redis mock
class MockRedis:
    def __init__(self):
        self._data = {}
        self._expires = {}
    
    def get(self, key: str):
        if key in self._expires and datetime.utcnow() > self._expires[key]:
            del self._data[key]
            del self._expires[key]
            return None
        return self._data.get(key)
    
    def set(self, key: str, value: str):
        self._data[key] = value
    
    def setex(self, key: str, seconds: int, value: str):
        self._data[key] = value
        self._expires[key] = datetime.utcnow() + timedelta(seconds=seconds)
    
    def incr(self, key: str):
        current = int(self._data.get(key, 0))
        self._data[key] = str(current + 1)
        return current + 1
    
    def expire(self, key: str, seconds: int):
        if key in self._data:
            self._expires[key] = datetime.utcnow() + timedelta(seconds=seconds)
    
    def delete(self, key: str):
        self._data.pop(key, None)
        self._expires.pop(key, None)
    
    def exists(self, key: str):
        return key in self._data
    
    def ping(self):
        return True
    
    def hset(self, key: str, mapping: Dict[str, str]):
        self._data[key] = json.dumps(mapping)
    
    def hgetall(self, key: str):
        data = self._data.get(key)
        return json.loads(data) if data else {}
    
    def lpush(self, key: str, value: str):
        current = self._data.get(key, [])
        if isinstance(current, str):
            current = json.loads(current)
        current.insert(0, value)
        self._data[key] = json.dumps(current)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    return MockRedis()


@pytest_asyncio.fixture
async def test_client(test_db_session, mock_redis):
    """Create test client with overridden dependencies."""
    
    # Override database dependency
    app.dependency_overrides[get_db] = lambda: test_db_session
    
    # Create async client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_enterprise_client(test_db_session) -> EnterpriseClient:
    """Create test enterprise client."""
    client = EnterpriseClient(
        company_name="Test Corp",
        legal_entity_name="Test Corporation Limited",
        registration_number="TC123456",
        tax_id="TAX123456",
        primary_contact_name="John Doe",
        primary_contact_email="john@testcorp.com",
        primary_contact_phone="+1234567890",
        address_line1="123 Test Street",
        city="Test City",
        state="Test State",
        country="Test Country",
        postal_code="12345",
        tier="enterprise",
        is_active=True,
        is_verified=True,
        api_rate_limit=10000,
        max_api_keys=50,
        max_users=200
    )
    
    test_db_session.add(client)
    await test_db_session.commit()
    await test_db_session.refresh(client)
    
    return client


@pytest_asyncio.fixture
async def test_user(test_db_session, test_enterprise_client) -> User:
    """Create test user."""
    user = User(
        client_id=test_enterprise_client.id,
        email="testuser@testcorp.com",
        full_name="Test User",
        phone_number="+1234567890",
        is_active=True,
        is_admin=True,
        email_verified=True
    )
    
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def test_api_key(test_db_session, test_enterprise_client) -> APIKey:
    """Create test API key."""
    import hashlib
    
    api_key_value = "gw_test_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
    
    api_key = APIKey(
        client_id=test_enterprise_client.id,
        key_hash=key_hash,
        key_prefix=api_key_value[:8],
        name="Test API Key",
        permissions=["ai_suite.*", "anonymous_services.*", "trading.*", "banking.*"],
        rate_limit=5000,
        is_active=True
    )
    
    test_db_session.add(api_key)
    await test_db_session.commit()
    await test_db_session.refresh(api_key)
    
    # Store the actual key value for tests
    api_key._test_key_value = api_key_value
    
    return api_key


@pytest_asyncio.fixture
async def test_b2b_services(test_db_session) -> list[B2BService]:
    """Create test B2B services."""
    services = [
        B2BService(
            service_type="ai_suite",
            name="ai_support_engine",
            display_name="AI Support Engine",
            description="Multi-language AI support with financial expertise",
            features={
                "languages": 11,
                "accuracy": 0.99,
                "response_time": "1.2s"
            },
            pricing={
                "growth": {"monthly": 50000, "annual": 500000},
                "enterprise": {"monthly": 200000, "annual": 2000000},
                "quantum": {"monthly": 1000000, "annual": 10000000}
            },
            is_active=True
        ),
        B2BService(
            service_type="anonymous_services",
            name="zk_portfolio_management",
            display_name="Anonymous Portfolio Management",
            description="Zero-knowledge portfolio verification",
            features={
                "privacy_tiers": ["onyx", "obsidian", "void"],
                "quantum_resistant": True,
                "emergency_reveal": True
            },
            pricing={
                "obsidian": {"monthly": 500000, "annual": 5000000},
                "void": {"monthly": 2000000, "annual": 20000000}
            },
            is_active=True
        ),
        B2BService(
            service_type="trading_as_service",
            name="multi_exchange_trading",
            display_name="Multi-Exchange Trading",
            description="Enterprise trading infrastructure",
            features={
                "exchanges": ["NSE", "BSE", "MCX"],
                "execution_time": "sub_millisecond",
                "risk_management": True
            },
            pricing={
                "growth": {"monthly": 100000, "annual": 1000000},
                "enterprise": {"monthly": 500000, "annual": 5000000}
            },
            is_active=True
        ),
        B2BService(
            service_type="banking_as_service",
            name="payment_processing",
            display_name="Payment Processing",
            description="Multi-currency payment infrastructure",
            features={
                "currencies": ["INR", "USD", "EUR", "GBP"],
                "settlement": "real_time",
                "compliance": "global"
            },
            pricing={
                "growth": {"monthly": 75000, "annual": 750000},
                "enterprise": {"monthly": 300000, "annual": 3000000}
            },
            is_active=True
        )
    ]
    
    for service in services:
        test_db_session.add(service)
    
    await test_db_session.commit()
    
    for service in services:
        await test_db_session.refresh(service)
    
    return services


@pytest.fixture
def mock_auth_user(test_user, test_enterprise_client):
    """Mock authenticated user for dependency injection."""
    from ..auth.enterprise_auth import TokenData
    
    return TokenData(
        client_id=str(test_enterprise_client.id),
        user_id=str(test_user.id),
        email=test_user.email,
        roles=["admin"],
        permissions=["ai_suite.*", "anonymous_services.*", "trading.*", "banking.*"],
        tier=test_enterprise_client.tier,
        exp=datetime.utcnow() + timedelta(hours=24)
    )


@pytest.fixture
def mock_api_key_data(test_api_key, test_enterprise_client):
    """Mock API key data for dependency injection."""
    from ..auth.enterprise_auth import APIKeyData
    
    return APIKeyData(
        key_id=str(test_api_key.id),
        client_id=str(test_enterprise_client.id),
        name=test_api_key.name,
        permissions=test_api_key.permissions,
        rate_limit=test_api_key.rate_limit,
        expires_at=None
    )


@pytest.fixture
def override_auth_dependencies(mock_auth_user, mock_api_key_data):
    """Override authentication dependencies for testing."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_api_key_data] = lambda: mock_api_key_data
    
    yield
    
    # Clean up
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    if get_api_key_data in app.dependency_overrides:
        del app.dependency_overrides[get_api_key_data]


# Mock AI service engines for testing
@pytest.fixture
def mock_support_engine():
    """Mock AI Support Engine."""
    mock = AsyncMock()
    mock.process_support_request.return_value = MagicMock(
        request_id="test_req_123",
        response_text="Test AI response",
        language="en",
        confidence_score=0.95,
        response_time_ms=1200,
        model_used="gpt-4-turbo",
        follow_up_suggestions=["Test suggestion 1", "Test suggestion 2"],
        response_audio=None
    )
    return mock


@pytest.fixture
def mock_intelligence_engine():
    """Mock AI Intelligence Engine."""
    mock = AsyncMock()
    mock.process_intelligence_request.return_value = MagicMock(
        intelligence_type="morning_pulse",
        market_region="india",
        summary="Test market summary",
        key_insights=["Insight 1", "Insight 2"],
        data_points={"test": "data"},
        confidence_score=0.92,
        risk_level="low",
        actionable_recommendations=["Recommendation 1"],
        timestamp=datetime.utcnow(),
        supporting_data={"source": "test"}
    )
    return mock


@pytest.fixture
def mock_moderator_engine():
    """Mock AI Moderator Engine."""
    mock = AsyncMock()
    mock.moderate_content.return_value = MagicMock(
        request_id="mod_test_123",
        action="allow",
        confidence_score=0.98,
        spam_categories=[],
        risk_level="low",
        explanation="Content is safe",
        processing_time_ms=45,
        escalation_required=False,
        recommended_actions=[]
    )
    return mock


@pytest.fixture
def mock_zk_proof_system():
    """Mock ZK Proof System."""
    mock = AsyncMock()
    mock.generate_zk_proof.return_value = MagicMock(
        proof_id="zkp_test_123",
        status="verified",
        proof_data={"test": "proof"},
        verification_hash="test_hash_123",
        confidence_score=0.99,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        emergency_recovery_hash="emergency_hash_123"
    )
    mock.verify_zk_proof.return_value = (True, 0.99)
    return mock


@pytest.fixture
def mock_anonymous_portfolio_manager():
    """Mock Anonymous Portfolio Manager."""
    mock = AsyncMock()
    mock.create_anonymous_identity.return_value = MagicMock(
        identity_id="anon_test_123",
        privacy_tier="obsidian",
        public_key=b"test_public_key",
        proof_requirements=["portfolio_ownership", "net_worth_threshold"],
        emergency_contacts=["contact@test.com"],
        created_at=datetime.utcnow(),
        last_verified=datetime.utcnow()
    )
    return mock


@pytest.fixture
def override_service_dependencies(
    mock_support_engine,
    mock_intelligence_engine,
    mock_moderator_engine,
    mock_zk_proof_system,
    mock_anonymous_portfolio_manager
):
    """Override all service dependencies for testing."""
    app.dependency_overrides[get_support_engine] = lambda: mock_support_engine
    app.dependency_overrides[get_intelligence_engine] = lambda: mock_intelligence_engine
    app.dependency_overrides[get_moderator_engine] = lambda: mock_moderator_engine
    app.dependency_overrides[get_zk_proof_system] = lambda: mock_zk_proof_system
    app.dependency_overrides[get_anonymous_portfolio_manager] = lambda: mock_anonymous_portfolio_manager
    
    yield {
        "support_engine": mock_support_engine,
        "intelligence_engine": mock_intelligence_engine,
        "moderator_engine": mock_moderator_engine,
        "zk_proof_system": mock_zk_proof_system,
        "anonymous_portfolio_manager": mock_anonymous_portfolio_manager
    }
    
    # Clean up
    for dependency in [
        get_support_engine,
        get_intelligence_engine,
        get_moderator_engine,
        get_zk_proof_system,
        get_anonymous_portfolio_manager
    ]:
        if dependency in app.dependency_overrides:
            del app.dependency_overrides[dependency]


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_portfolio_data():
        """Create test portfolio data."""
        return {
            "holdings": [
                {"id": "holding_1", "symbol": "INFY", "value": 1000000},
                {"id": "holding_2", "symbol": "TCS", "value": 1500000},
                {"id": "holding_3", "symbol": "RELIANCE", "value": 2000000}
            ],
            "total_value": 4500000,
            "currency": "INR"
        }
    
    @staticmethod
    def create_market_data():
        """Create test market data."""
        return {
            "nifty_50": 21500.0,
            "sensex": 71000.0,
            "bank_nifty": 46500.0,
            "volatility": "moderate",
            "session": "open"
        }
    
    @staticmethod
    def create_ai_context():
        """Create test AI context."""
        return {
            "conversation_history": [
                {"role": "user", "content": "What is NIFTY?"},
                {"role": "assistant", "content": "NIFTY is the National Stock Exchange index."}
            ],
            "user_preferences": {"language": "en", "complexity": "advanced"},
            "session_id": "test_session_123"
        }


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory


# Performance testing fixtures
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "concurrent_users": 100,
        "test_duration": 60,  # seconds
        "ramp_up_time": 10,   # seconds
        "target_response_time": 200,  # milliseconds
        "error_threshold": 0.01  # 1% error rate
    }


# Security testing fixtures
@pytest.fixture
def security_test_payloads():
    """Security test payloads for penetration testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    }


# Coverage tracking
@pytest.fixture(autouse=True)
def coverage_tracking():
    """Automatically track test coverage."""
    import coverage
    
    cov = coverage.Coverage()
    cov.start()
    
    yield
    
    cov.stop()
    # Coverage reporting will be handled by pytest-cov plugin


# Cleanup fixture
@pytest.fixture(autouse=True)
async def cleanup_test_artifacts():
    """Clean up test artifacts after each test."""
    yield
    
    # Clean up any temporary files, clear caches, etc.
    # This runs after each test
    pass