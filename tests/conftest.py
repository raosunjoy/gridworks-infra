"""
Test configuration and fixtures for GridWorks Platform
Provides comprehensive test setup with mocked dependencies and test data
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
import json
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.charting.core.chart_engine import OHLCV, ChartConfig, TimeFrame
from app.models.charts import Chart, ChartDrawing, ChartAnnotation
from app.models.users import User, UserProfile
from app.models.social import ExpertProfile, CollaborationSession
from app.models.marketplace import TradingIdea, IdeaSubscription

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(db_session):
    """Create test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# User fixtures
@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        display_name="Test User",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def expert_user(db_session):
    """Create expert user with profile"""
    user = User(
        id=str(uuid.uuid4()),
        email="expert@example.com",
        display_name="Expert Trader",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    
    expert_profile = ExpertProfile(
        id=str(uuid.uuid4()),
        user_id=user.id,
        specialization=json.dumps(["NIFTY", "OPTIONS"]),
        years_experience=5,
        trading_style="Swing Trading",
        bio="Professional trader with 5 years experience",
        application_status="APPROVED",
        is_active=True,
        verified_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(expert_profile)
    db_session.commit()
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    return {"Authorization": f"Bearer test_token_{test_user.id}"}

@pytest.fixture
def expert_auth_headers(expert_user):
    """Create authentication headers for expert user"""
    return {"Authorization": f"Bearer test_token_{expert_user.id}"}

# Chart fixtures
@pytest.fixture
def chart_config():
    """Create test chart configuration"""
    return ChartConfig(
        symbol="RELIANCE",
        timeframe=TimeFrame.FIVE_MINUTES,
        kagi_reversal=1.0,
        kagi_reversal_type="percentage",
        range_size=5.0,
        range_type="points"
    )

@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing"""
    base_time = datetime(2024, 1, 1, 9, 15)
    data = []
    
    for i in range(100):
        timestamp = base_time + timedelta(minutes=i * 5)
        # Create realistic price movement
        base_price = 2500 + (i * 2) + (i % 10 - 5) * 3
        
        data.append(OHLCV(
            timestamp=timestamp,
            open=base_price,
            high=base_price + abs(i % 7) * 2,
            low=base_price - abs(i % 5) * 1.5,
            close=base_price + (i % 3 - 1) * 2,
            volume=10000 + (i % 20) * 1000
        ))
    
    return data

@pytest.fixture
def test_chart(db_session, test_user):
    """Create test chart"""
    chart = Chart(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        symbol="RELIANCE",
        timeframe="5m",
        chart_type="candlestick",
        settings=json.dumps({"theme": "dark"}),
        is_public=False,
        created_at=datetime.utcnow()
    )
    db_session.add(chart)
    db_session.commit()
    return chart

@pytest.fixture
def test_drawing(db_session, test_chart):
    """Create test chart drawing"""
    drawing = ChartDrawing(
        id=str(uuid.uuid4()),
        chart_id=test_chart.id,
        user_id=test_chart.user_id,
        drawing_type="trend_line",
        drawing_data=json.dumps({
            "points": [{"x": 0, "y": 2500}, {"x": 100, "y": 2600}],
            "style": {"color": "#00ff00", "width": 2}
        }),
        is_public=True,
        created_at=datetime.utcnow()
    )
    db_session.add(drawing)
    db_session.commit()
    return drawing

# Trading idea fixtures
@pytest.fixture
def sample_trading_idea(db_session, expert_user):
    """Create sample trading idea"""
    idea = TradingIdea(
        id=str(uuid.uuid4()),
        expert_user_id=expert_user.id,
        title="RELIANCE Bullish Breakout",
        description="Strong breakout above resistance with high volume confirmation",
        idea_type="TRADE_SIGNAL",
        category="EQUITY",
        symbol="RELIANCE",
        target_price=2800.0,
        stop_loss=2450.0,
        entry_price=2500.0,
        risk_level="MEDIUM",
        time_horizon="SHORT_TERM",
        expected_returns="10-12%",
        technical_rationale="RSI oversold, MACD bullish crossover, volume breakout",
        is_premium=True,
        premium_price=Decimal("99.00"),
        tags=json.dumps(["breakout", "volume", "technical"]),
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    db_session.add(idea)
    db_session.commit()
    return idea

# Mock fixtures
@pytest.fixture
def mock_whatsapp_client():
    """Mock WhatsApp client"""
    mock = AsyncMock()
    mock.send_message.return_value = "whatsapp_msg_123"
    mock.send_image.return_value = "whatsapp_img_123"
    return mock

@pytest.fixture
def mock_trading_engine():
    """Mock trading engine"""
    mock = AsyncMock()
    mock.get_current_price.return_value = 2500.0
    mock.execute_trade.return_value = {
        "success": True,
        "trade_id": "trade_123",
        "status": "FILLED"
    }
    return mock

@pytest.fixture
def mock_risk_manager():
    """Mock risk manager"""
    mock = AsyncMock()
    mock.validate_trade.return_value = {
        "approved": True,
        "reason": None
    }
    mock.calculate_position_size.return_value = 10
    return mock

@pytest.fixture
def mock_zk_verification():
    """Mock ZK verification service"""
    mock = AsyncMock()
    mock.generate_copy_proof.return_value = "zk_proof_abc123"
    mock.generate_idea_proof.return_value = "zk_proof_idea_xyz789"
    return mock

@pytest.fixture
def mock_notification_service():
    """Mock notification service"""
    mock = AsyncMock()
    mock.send_collaboration_invite.return_value = True
    mock.send_new_idea_notification.return_value = True
    return mock

@pytest.fixture
def mock_payment_processor():
    """Mock payment processor"""
    mock = AsyncMock()
    mock.process_subscription_payment.return_value = {
        "success": True,
        "transaction_id": "txn_123456",
        "amount": Decimal("999.00")
    }
    return mock

# WebSocket fixtures
@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    mock = AsyncMock()
    mock.accept = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock()
    mock.close = AsyncMock()
    mock.client_state = Mock()
    mock.client_state.DISCONNECTED = "DISCONNECTED"
    return mock

# Test data generators
@pytest.fixture
def kagi_test_data():
    """Generate test data for Kagi charts"""
    return [
        {"price": 100.0, "timestamp": datetime(2024, 1, 1, 9, 15)},
        {"price": 102.0, "timestamp": datetime(2024, 1, 1, 9, 20)},
        {"price": 98.0, "timestamp": datetime(2024, 1, 1, 9, 25)},
        {"price": 104.0, "timestamp": datetime(2024, 1, 1, 9, 30)},
        {"price": 101.0, "timestamp": datetime(2024, 1, 1, 9, 35)},
        {"price": 106.0, "timestamp": datetime(2024, 1, 1, 9, 40)},
        {"price": 103.0, "timestamp": datetime(2024, 1, 1, 9, 45)},
        {"price": 108.0, "timestamp": datetime(2024, 1, 1, 9, 50)},
    ]

@pytest.fixture
def range_bars_test_data():
    """Generate test data for Range Bars charts"""
    base_time = datetime(2024, 1, 1, 9, 15)
    data = []
    
    prices = [2500, 2502, 2505, 2503, 2508, 2506, 2510, 2512, 2509, 2515]
    
    for i, price in enumerate(prices):
        data.append({
            "timestamp": base_time + timedelta(minutes=i),
            "close": price,
            "volume": 1000 + i * 100
        })
    
    return data

# Performance test fixtures
@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing"""
    base_time = datetime(2024, 1, 1, 9, 15)
    data = []
    
    for i in range(10000):  # 10k data points
        timestamp = base_time + timedelta(seconds=i * 10)
        base_price = 2500 + (i * 0.1) + (i % 100 - 50) * 0.5
        
        data.append(OHLCV(
            timestamp=timestamp,
            open=base_price,
            high=base_price + abs(i % 10) * 0.5,
            low=base_price - abs(i % 8) * 0.3,
            close=base_price + (i % 5 - 2) * 0.2,
            volume=1000 + (i % 50) * 100
        ))
    
    return data

# Error simulation fixtures
@pytest.fixture
def database_error_simulation():
    """Simulate database errors for testing error handling"""
    def simulate_error():
        raise Exception("Database connection failed")
    return simulate_error

@pytest.fixture
def network_error_simulation():
    """Simulate network errors for testing resilience"""
    def simulate_error():
        raise Exception("Network timeout")
    return simulate_error

# Test utilities
@pytest.fixture
def assert_helpers():
    """Helper functions for test assertions"""
    class AssertHelpers:
        @staticmethod
        def assert_chart_data_valid(chart_data):
            """Assert chart data structure is valid"""
            assert "chart_id" in chart_data
            assert "chart_type" in chart_data
            assert "symbol" in chart_data
            assert isinstance(chart_data.get("analytics", {}), dict)
        
        @staticmethod
        def assert_api_response_structure(response, expected_fields):
            """Assert API response has expected structure"""
            assert response.status_code == 200
            data = response.json()
            for field in expected_fields:
                assert field in data
        
        @staticmethod
        def assert_performance_metrics(metrics, max_time_ms=1000):
            """Assert performance metrics meet requirements"""
            if "calculation_time_ms" in metrics:
                assert metrics["calculation_time_ms"] < max_time_ms
            if "average_calculation_time_ms" in metrics:
                assert metrics["average_calculation_time_ms"] < max_time_ms
        
        @staticmethod
        def assert_pattern_detection(patterns, expected_pattern_types):
            """Assert pattern detection results"""
            assert isinstance(patterns, list)
            for pattern in patterns:
                assert "pattern" in pattern
                assert "confidence" in pattern
                assert 0 <= pattern["confidence"] <= 1
                if expected_pattern_types:
                    assert pattern["pattern"] in expected_pattern_types
    
    return AssertHelpers()

# Integration test fixtures
@pytest.fixture
def integration_test_setup(db_session, test_user, expert_user):
    """Setup for integration tests with multiple components"""
    # Create test chart
    chart = Chart(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        symbol="NIFTY",
        timeframe="15m",
        chart_type="kagi",
        created_at=datetime.utcnow()
    )
    db_session.add(chart)
    
    # Create expert drawing
    drawing = ChartDrawing(
        id=str(uuid.uuid4()),
        chart_id=chart.id,
        user_id=expert_user.id,
        drawing_type="support_line",
        drawing_data=json.dumps({"level": 18500, "strength": 0.85}),
        is_public=True,
        created_at=datetime.utcnow()
    )
    db_session.add(drawing)
    
    # Create trading idea
    idea = TradingIdea(
        id=str(uuid.uuid4()),
        expert_user_id=expert_user.id,
        title="NIFTY Support Bounce",
        description="Expecting bounce from key support level",
        idea_type="TECHNICAL_ANALYSIS",
        category="INDEX",
        symbol="NIFTY",
        target_price=19000.0,
        stop_loss=18300.0,
        entry_price=18500.0,
        risk_level="MEDIUM",
        time_horizon="SHORT_TERM",
        technical_rationale="Strong support level with multiple tests",
        is_premium=False,
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    db_session.add(idea)
    
    db_session.commit()
    
    return {
        "chart": chart,
        "drawing": drawing,
        "idea": idea,
        "test_user": test_user,
        "expert_user": expert_user
    }

# Patch decorators for consistent mocking
@pytest.fixture
def mock_external_services():
    """Mock all external services consistently across tests"""
    with patch.multiple(
        'app.services',
        whatsapp_client=AsyncMock(),
        trading_engine=AsyncMock(),
        risk_manager=AsyncMock(),
        payment_processor=AsyncMock(),
        notification_service=AsyncMock(),
        zk_verification=AsyncMock()
    ) as mocks:
        yield mocks