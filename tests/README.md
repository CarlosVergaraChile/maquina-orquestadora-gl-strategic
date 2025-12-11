# Tests - Máquina Orquestadora GL Strategic

## Overview

This directory contains comprehensive stress testing and validation test suites for the Máquina Orquestadora GL Strategic v2.2 system.

## Files

### `test_stress_framework.py` (300+ lines)
Comprehensive stress testing framework including:

- **StressTestMetrics**: Performance metrics tracking (response times, error rates, percentiles)
- **MultiModelOrchestrationTest**: Tests for concurrent multi-model orchestration
- **ContextManagementTest**: Tests for extreme context scenarios (100k tokens, empty, corrupted)
- **AdaptiveControlTest**: Tests for real-time parameter changes
- **PerformanceTest**: Performance SLA validation and memory efficiency tests

### `conftest.py` (120+ lines)
Pytest configuration and fixtures:

- Event loop fixture for async tests
- Mock context fixture for testing
- Large context fixture (100k tokens)
- Metrics tracker fixture
- Model configuration fixture

## Running Tests

### Install dependencies
```bash
pip install pytest pytest-asyncio pytest-timeout
```

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Stress tests only
pytest -m stress

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Run with verbose output
```bash
pytest -v --tb=short
```

### Run with coverage
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### Run with specific verbosity
```bash
# Very verbose
pytest -vv

# With print statements
pytest -s

# With print and verbose
pytest -vs
```

## Test Markers

Tests are organized with pytest markers:

- `@pytest.mark.stress` - Stress testing tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.concurrent` - Async/concurrent tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.edge_case` - Edge case tests

## Configuration

Pytest configuration is in `pytest.ini` in the project root:

- Test discovery patterns
- Custom markers
- Output options
- Asyncio mode configuration
- Test timeout (300 seconds)
- Logging configuration

## Expected Test Results

When running tests, you should see:

```
=== Multi-Model Orchestration Results ===
- success_rate: 100%
- avg_latency_ms: ~1500
- throughput_rps: ~30

=== Context Management Results ===
- Large context (100k tokens): Handled successfully
- Empty context: Handled successfully
- Corrupted context: Recovered successfully

=== Adaptive Control Results ===
- Temperature range (0.0-2.0): All values valid
- Concurrent parameter changes: All updated correctly

=== Performance Results ===
- Response time SLA (<2s): MET
- Memory efficiency: ~50 bytes/token
```

## Adding New Tests

1. Create new test file: `test_*.py`
2. Import fixtures from `conftest.py`
3. Use appropriate markers
4. Run `pytest --collect-only` to verify discovery

## CI/CD Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-timeout

# Run tests with XML output
pytest --junit-xml=test-results.xml

# Run with coverage
pytest --cov=app --cov-report=xml
```

## Troubleshooting

### Event loop errors
```bash
pip install pytest-asyncio
```

### Timeout errors
Increase timeout in `pytest.ini` if tests are running slow

### Import errors
Ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

## Performance Baselines

- **P99 Latency**: < 2000ms
- **Success Rate**: > 99%
- **Memory/Context**: < 100 bytes per token
- **Concurrent Requests**: 50+ simultaneous

## Future Test Coverage

- [ ] API endpoint integration tests
- [ ] Database transaction tests
- [ ] Authentication/authorization tests
- [ ] Rate limiting tests
- [ ] Load testing with 1000+ concurrent requests
- [ ] Security penetration tests
- [ ] Frontend UI tests (Selenium/Cypress)

---

For more information, see [PROJECT_STATUS_v2.2.md](../PROJECT_STATUS_v2.2.md)
