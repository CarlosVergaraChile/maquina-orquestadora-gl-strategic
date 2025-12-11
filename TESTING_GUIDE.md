# Testing Guide - Máquina Orquestadora GL Strategic v2.2

## Quick Start

### 1. Install Testing Dependencies

```bash
cd maquina-orquestadora-gl-strategic
pip install pytest pytest-asyncio pytest-timeout
```

### 2. Run All Tests

```bash
pytest
```

### 3. View Results

You should see output like:
```
========================== test session starts ==========================
collected 8 items

tests/test_stress_framework.py::test_context_management PASSED   [12%]
tests/test_stress_framework.py::test_adaptive_control PASSED     [25%]
tests/test_stress_framework.py::test_performance PASSED          [37%]
...
```

## Comprehensive Test Framework

The testing framework includes 4 main components:

### 1. **test_stress_framework.py** (300+ lines)
- **StressTestMetrics**: Tracks response times, success rates, percentiles (P50/P95/P99)
- **MultiModelOrchestrationTest**: Tests 3-model orchestration with concurrent requests
- **ContextManagementTest**: Tests extreme scenarios (100k tokens, empty, corrupted)
- **AdaptiveControlTest**: Tests real-time parameter changes
- **PerformanceTest**: Validates SLA compliance and memory efficiency

### 2. **conftest.py** (120+ lines)
Provides pytest fixtures:
- `event_loop`: Async test support
- `mock_context`: Test conversation context
- `large_context`: 100,000 token context
- `metrics_tracker`: Performance tracking
- `model_config`: LLM model configuration

### 3. **pytest.ini** (50 lines)
Pytest configuration:
- Test discovery patterns
- Custom markers (stress, performance, slow, concurrent, etc.)
- Logging and output options
- Timeout configuration (300 seconds)
- Asyncio mode

### 4. **tests/README.md** (175+ lines)
Detailed testing documentation with:
- Usage instructions
- Test markers explanation
- Expected test results
- CI/CD integration
- Troubleshooting guide

## Running Specific Tests

### By Category

```bash
# Stress tests only
pytest -m stress

# Performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"

# Concurrent/async tests
pytest -m concurrent
```

### By File

```bash
# Run single test file
pytest tests/test_stress_framework.py

# Run single test function
pytest tests/test_stress_framework.py::test_context_management
```

### With Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Show test names only (no output)
pytest -q

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

## Performance Baselines

When tests pass, you should see these metrics:

```
=== Multi-Model Orchestration ===
- Duration: ~2-3 seconds
- Total Requests: 50
- Success Rate: 100%
- Throughput: ~25-30 requests/second
- P99 Latency: ~1500ms

=== Context Management ===
- Large Context (100k tokens): Handled ✓
- Empty Context: Handled ✓
- Corrupted Context: Recovered ✓

=== Adaptive Control ===
- Temperature Range (0.0-2.0): All valid ✓
- Concurrent Parameter Changes: All applied ✓
- Avg Update Time: ~10ms

=== Performance ===
- Response Time SLA (<2s): MET ✓
- Memory Efficiency: ~50 bytes/token ✓
```

## Stress Test Scenarios

The framework tests these critical scenarios:

### 1. Multi-Model Orchestration Under Load
- **Scenario**: 50 concurrent requests across 3 models
- **Model Latencies**:
  - Claude: 1000-2000ms
  - GPT-4: 500-1000ms
  - Gemini: 1500-3000ms
- **Expected**: All responses collected, aggregated, returned within 4s

### 2. Extreme Context Management
- **100,000 Token Context**: Verify handling of massive contexts
- **Empty Context**: Ensure graceful handling
- **Corrupted Data**: Test recovery mechanisms
- **Expected**: No memory overflow, < 2s response time

### 3. Real-Time Adaptive Control
- **Temperature Changes**: 0.0 → 2.0 dynamically
- **Top-P Adjustments**: 0.0 → 1.0 adjustments
- **Concurrent Updates**: 10 simultaneous conversations
- **Expected**: All parameters applied correctly

### 4. Performance SLA Validation
- **Response Time**: P99 latency < 2000ms
- **Success Rate**: > 99% successful responses
- **Memory Usage**: < 100 bytes per token
- **Concurrent Requests**: Support 50+ simultaneous

## CI/CD Integration

To integrate tests into your CI/CD pipeline:

```bash
#!/bin/bash
# Install dependencies
pip install pytest pytest-asyncio pytest-timeout

# Run tests with XML output
pytest --junit-xml=test-results.xml

# Run with coverage
pip install pytest-cov
pytest --cov=app --cov-report=xml --cov-report=html

# Check coverage threshold
pytest --cov=app --cov-fail-under=70
```

## Troubleshooting

### Event Loop Errors
```bash
pip install pytest-asyncio==0.21.1
export PYTEST_ASYNCIO_MODE=auto
pytest
```

### Timeout Errors
Increase timeout in `pytest.ini`:
```ini
timeout = 600  # 10 minutes
```

### Import Path Issues
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Memory Issues with Large Context Tests
```bash
# Run only fast tests
pytest -m "not slow"

# Or with memory limit
memory_profiler -m pytest tests/test_stress_framework.py
```

## Adding New Tests

1. **Create test file**: `tests/test_new_feature.py`
2. **Use fixtures** from conftest.py:
   ```python
   def test_my_feature(mock_context, metrics_tracker):
       metrics_tracker.record("latency", 0.5)
       assert mock_context["conversation_id"] == "test-123"
   ```
3. **Add markers**:
   ```python
   @pytest.mark.stress
   @pytest.mark.performance
   async def test_my_stress_test():
       ...
   ```
4. **Run discovery**: `pytest --collect-only`

## Performance Profiling

### Profile Test Execution Time
```bash
pytest --durations=10
```

### Memory Profiling
```bash
pip install memory-profiler
python -m memory_profiler tests/test_stress_framework.py
```

### CPU Profiling
```bash
pip install py-spy
py-spy record -o profile.svg -- pytest tests/test_stress_framework.py
```

## Test Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View report
```

## Related Documentation

- [PROJECT_STATUS_v2.2.md](./PROJECT_STATUS_v2.2.md) - Project status and roadmap
- [IMPROVEMENTS.md](./IMPROVEMENTS.md) - Feature improvements
- [QUICK_START.md](./QUICK_START.md) - Quick start guide
- [tests/README.md](./tests/README.md) - Detailed testing documentation

## Support

For issues or questions:
1. Check [tests/README.md](./tests/README.md)
2. Review test output carefully
3. Run with `-vv` for verbose output
4. Check `pytest.ini` configuration

---

**Last Updated**: December 2024
**Version**: 2.2
**Status**: Production Ready
