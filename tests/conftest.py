"""Pytest configuration and fixtures for Máquina Orquestadora testing"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch
import os

# ============================================================================
# PYTEST CONFIGURATION & MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, <1s)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (slower, >1s)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (very slow, API calls)"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

# ============================================================================
# EVENT LOOP FOR ASYNC TESTS
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# ============================================================================
# MOCK FIXTURES (Unit Testing)
# ============================================================================

@pytest.fixture
def mock_claude_api():
    """Mock Claude API for fast unit tests"""
    with patch('app.backend.claude_integration.Anthropic') as mock:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Mock response from Claude")],
            usage=MagicMock(output_tokens=100, input_tokens=50),
            stop_reason="end_turn"
        )
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def mock_database():
    """Mock database for fast unit tests"""
    with patch('app.backend.database.sqlite3.connect') as mock:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock.return_value = mock_conn
        yield mock

@pytest.fixture
def mock_orchestrator(mock_claude_api):
    """Mock orchestrator instance"""
    return MagicMock(
        api_key="mock-key",
        client=mock_claude_api.return_value,
        conversation_history=[],
        model="claude-3-5-sonnet-20241022"
    )

# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_context():
    """Provide standard test context"""
    return {
        "conversation_id": "test-123",
        "user_id": "user-456",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ],
        "timestamp": datetime.now().isoformat(),
    }

@pytest.fixture
def sample_api_response():
    """Provide sample API response"""
    return {
        "response": "This is a test response from Claude",
        "model": "claude-3-5-sonnet-20241022",
        "timestamp": datetime.now().isoformat(),
        "latency_ms": 150,
        "tokens_used": 50,
        "input_tokens": 25,
        "stop_reason": "end_turn",
        "success": True,
    }

@pytest.fixture
def mock_health_check():
    """Mock health check result"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "claude_api": "ready",
            "auth": "enabled",
        },
    }

# ============================================================================
# ENVIRONMENT FIXTURES
# ============================================================================

@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-key-for-testing")
    monkeypatch.setenv("JWT_SECRET_KEY", "mock-secret-for-testing")
    monkeypatch.setenv("DATABASE_PATH", ":memory:")
    yield

# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_benchmark():
    """Measure test performance"""
    import time
    start = time.time()
    yield
    elapsed = time.time() - start
    if elapsed > 1.0:
        print(f"\n⚠️ Test took {elapsed:.2f}s (consider marking as @pytest.mark.slow)")

# ============================================================================
# AUTO-USE FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules between tests"""
    yield
    # Clean up any module-level state

# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their location"""
    for item in items:
        # Mark tests in specific directories
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

def pytest_runtest_logreport(report):
    """Log test results"""
    if report.when == "call":
        if report.outcome == "failed":
            # Could send to monitoring service here
            pass

# ============================================================================
# SESSION SETUP/TEARDOWN
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """Set up test session"""
    os.environ["PYTEST_RUNNING"] = "true"
    yield
    # Cleanup after all tests
    if "PYTEST_RUNNING" in os.environ:
        del os.environ["PYTEST_RUNNING"]
