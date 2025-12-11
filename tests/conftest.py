"""Pytest configuration and fixtures for Máquina Orquestadora testing"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_context():
    """Provide mock conversation context"""
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
def large_context():
    """Provide large token context for stress testing"""
    return [f"token_{i}" for i in range(100000)]


@pytest.fixture
def metrics_tracker():
    """Provide metrics tracking instance"""
    class MetricsTracker:
        def __init__(self):
            self.data: Dict[str, List[float]] = {}
        
        def record(self, metric_name: str, value: float):
            if metric_name not in self.data:
                self.data[metric_name] = []
            self.data[metric_name].append(value)
        
        def get_stats(self, metric_name: str) -> Dict[str, float]:
            if metric_name not in self.data or not self.data[metric_name]:
                return {}
            
            values = sorted(self.data[metric_name])
            n = len(values)
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / n,
                "p50": values[int(n * 0.5)],
                "p95": values[int(n * 0.95)],
                "p99": values[int(n * 0.99)],
            }
    
    return MetricsTracker()


@pytest.fixture
def model_config():
    """Provide model configuration"""
    return {
        "models": [
            {
                "name": "Claude",
                "provider": "Anthropic",
                "latency_ms": [1000, 2000],
                "timeout_s": 30,
            },
            {
                "name": "GPT-4",
                "provider": "OpenAI",
                "latency_ms": [500, 1000],
                "timeout_s": 30,
            },
            {
                "name": "Gemini",
                "provider": "Google",
                "latency_ms": [1500, 3000],
                "timeout_s": 45,
            },
        ],
        "timeout_s": 30,
        "retry_count": 3,
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m "not slow"')"
    )
    config.addinivalue_line(
        "markers", "stress: marks tests as stress tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        if "stress" in item.nodeid:
            item.add_marker(pytest.mark.stress)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
