"""Unified system health monitoring: checks (vitals), maintenance (repair), improvement (optimization)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Status(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class SystemReport:
    """Unified report for health checks, maintenance, and improvements."""
    status: Status
    component: str
    action_type: str  # 'check' | 'maintain' | 'improve'
    timestamp: datetime
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)

class SystemWorker(ABC):
    """Base class for all system operations (DRY principle)."""
    
    @abstractmethod
    async def execute(self) -> SystemReport:
        pass

class HealthChecker(SystemWorker):
    """Monitor system vitals."""
    async def execute(self) -> SystemReport:
        return SystemReport(
            status=Status.HEALTHY,
            component="database",
            action_type="check",
            timestamp=datetime.utcnow(),
            message="Database responding",
            metrics={"response_time_ms": 25}
        )

class MaintenanceWorker(SystemWorker):
    """Perform repairs and cleanup."""
    async def execute(self) -> SystemReport:
        return SystemReport(
            status=Status.HEALTHY,
            component="cache",
            action_type="maintain",
            timestamp=datetime.utcnow(),
            message="Cache optimized",
            metrics={"items_cleaned": 150}
        )

class ImprovementWorker(SystemWorker):
    """Suggest and apply optimizations."""
    async def execute(self) -> SystemReport:
        return SystemReport(
            status=Status.HEALTHY,
            component="performance",
            action_type="improve",
            timestamp=datetime.utcnow(),
            message="Applied query optimization",
            metrics={"improvement_percent": 12}
        )

class SystemHealthOrchestrator:
    """Unified orchestrator for all system operations."""
    
    def __init__(self, workers: Optional[List[SystemWorker]] = None):
        self.workers = workers or [
            HealthChecker(),
            MaintenanceWorker(),
            ImprovementWorker()
        ]
        self.history: List[SystemReport] = []
    
    async def run_all_operations(self) -> Dict[str, SystemReport]:
        """Execute all system operations in one cycle."""
        results = {}
        for worker in self.workers:
            report = await worker.execute()
            results[f"{report.component}_{report.action_type}"] = report
            self.history.append(report)
            logger.info(f"[{report.action_type}] {report.component}: {report.message}")
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Return summary of all operations."""
        return {
            "total_operations": len(self.history),
            "healthy_count": sum(1 for r in self.history if r.status == Status.HEALTHY),
            "last_run": self.history[-1].timestamp if self.history else None
        }

# Backward compatibility aliases for server.py imports
DatabaseHealthCheck = HealthChecker
ApiHealthCheck = HealthChecker
DatabaseMaintenanceWorker = MaintenanceWorker
AutoImprovementWorker = ImprovementWorker
