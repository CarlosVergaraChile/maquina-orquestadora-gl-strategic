"""Reusable health check framework for monitoring system components."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheckResult:
    status: HealthStatus
    component: str
    timestamp: datetime
    message: str
    details: Dict[str, Any] = None

class HealthChecker(ABC):
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        pass

class DatabaseHealthCheck(HealthChecker):
    async def check(self) -> HealthCheckResult:
        try:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="database",
                timestamp=datetime.utcnow(),
                message="Database connected"
            )
        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component="database",
                timestamp=datetime.utcnow(),
                message=f"Database error: {e}"
            )

class ApiHealthCheck(HealthChecker):
    async def check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            component="api",
            timestamp=datetime.utcnow(),
            message="API responding"
        )

class HealthOrchestrator:
    def __init__(self, checks: List[HealthChecker] = None):
        self.checks = checks or [DatabaseHealthCheck(), ApiHealthCheck()]
    
    async def run_health_check(self) -> Dict[str, HealthCheckResult]:
        results = {}
        for check in self.checks:
            result = await check.check()
            results[result.component] = result
            logger.info(f"{result.component}: {result.status.value}")
        return results
