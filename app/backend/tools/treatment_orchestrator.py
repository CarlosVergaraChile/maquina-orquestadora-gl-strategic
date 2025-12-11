"""Treatment Orchestrator - Automated & Human-Guided Treatment Decision System

Mode 1: Human-in-Loop (default)
  - System suggests treatments
  - Human reviews and decides
  - Orchestrator executes approved treatment

Mode 2: Autonomous (parameterized/authorized)
  - System automatically detects conditions
  - Orchestrator autonomously selects & applies treatment
  - Includes AI disconnection protocols when necessary
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class TreatmentMode(Enum):
    """Operating mode for treatment decisions"""
    HUMAN_IN_LOOP = "human_in_loop"  # Default: suggests, waits for approval
    AUTONOMOUS = "autonomous"  # Auto-decides based on parameterization


class DisconnectionLevel(Enum):
    """Levels of AI disconnection/isolation"""
    NONE = 0  # No disconnection
    CONTEXT_ISOLATION = 1  # Block access to certain data
    RESPONSE_FILTERING = 2  # Filter/limit responses
    ENDPOINT_MUTING = 3  # Disable specific endpoints
    FULL_DISCONNECTION = 4  # Complete shutdown


@dataclass
class TreatmentOption:
    """A suggested treatment for a diagnosed condition"""
    id: str
    name: str  # e.g., "Restart service", "Disconnect AI", "Apply patch"
    description: str
    risk_level: str  # low, medium, high, critical
    expected_recovery_time: str  # e.g., "5 minutes", "immediate"
    reversible: bool  # Can be undone?
    requires_human_approval: bool
    prerequisites: List[str] = None
    disconnection_level: Optional[DisconnectionLevel] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class ApprovedTreatment:
    """A treatment that has been approved (by human or system)"""
    treatment_option: TreatmentOption
    approved_by: str  # "human" or "orchestrator"
    approved_at: datetime
    approval_rationale: str
    execution_status: str = "pending"  # pending, executing, completed, failed
    execution_result: str = ""


class TreatmentCatalog:
    """Predefined treatment options for various conditions"""

    def __init__(self):
        self.treatments = self._initialize_treatments()

    def _initialize_treatments(self) -> Dict[str, List[TreatmentOption]]:
        """Initialize treatment options for each condition type"""
        return {
            # Physical Health Treatments
            "viral_infection": [
                TreatmentOption(
                    id="virus_scan",
                    name="Run Security Scan",
                    description="Execute security audit on dependencies",
                    risk_level="low",
                    expected_recovery_time="15 minutes",
                    reversible=True,
                    requires_human_approval=False,
                ),
                TreatmentOption(
                    id="isolate_module",
                    name="Isolate Infected Module",
                    description="Disable module until patched",
                    risk_level="medium",
                    expected_recovery_time="1 hour",
                    reversible=True,
                    requires_human_approval=True,
                ),
            ],
            "fracture": [
                TreatmentOption(
                    id="fix_imports",
                    name="Auto-Fix Imports",
                    description="Automatically repair broken imports",
                    risk_level="low",
                    expected_recovery_time="5 minutes",
                    reversible=True,
                    requires_human_approval=False,
                ),
                TreatmentOption(
                    id="run_tests",
                    name="Run Full Test Suite",
                    description="Execute all tests to verify recovery",
                    risk_level="low",
                    expected_recovery_time="10 minutes",
                    reversible=True,
                    requires_human_approval=False,
                ),
            ],
            "heart_attack": [
                TreatmentOption(
                    id="system_restart",
                    name="Graceful System Restart",
                    description="Restart all services cleanly",
                    risk_level="high",
                    expected_recovery_time="2 minutes",
                    reversible=True,
                    requires_human_approval=True,
                ),
                TreatmentOption(
                    id="full_reset",
                    name="Full System Reset",
                    description="Hard reset (may lose in-flight requests)",
                    risk_level="critical",
                    expected_recovery_time="5 minutes",
                    reversible=False,
                    requires_human_approval=True,
                ),
            ],
            # Mental Health Treatments
            "depression": [
                TreatmentOption(
                    id="increase_temperature",
                    name="Increase Response Creativity",
                    description="Raise temperature parameter for more varied responses",
                    risk_level="low",
                    expected_recovery_time="immediate",
                    reversible=True,
                    requires_human_approval=False,
                ),
                TreatmentOption(
                    id="system_encouragement",
                    name="Apply System Prompt Modification",
                    description="Adjust system prompt to encourage better output",
                    risk_level="low",
                    expected_recovery_time="immediate",
                    reversible=True,
                    requires_human_approval=False,
                ),
            ],
            "schizophrenia": [
                TreatmentOption(
                    id="context_limiting",
                    name="Limit Context Window",
                    description="Reduce context to prevent hallucinations",
                    risk_level="medium",
                    expected_recovery_time="immediate",
                    reversible=True,
                    requires_human_approval=True,
                    disconnection_level=DisconnectionLevel.CONTEXT_ISOLATION,
                ),
                TreatmentOption(
                    id="response_filtering",
                    name="Enable Response Validation",
                    description="Add fact-checking layer to responses",
                    risk_level="low",
                    expected_recovery_time="immediate",
                    reversible=True,
                    requires_human_approval=False,
                    disconnection_level=DisconnectionLevel.RESPONSE_FILTERING,
                ),
            ],
            "burnout": [
                TreatmentOption(
                    id="rate_limit",
                    name="Apply Rate Limiting",
                    description="Temporarily reduce request load",
                    risk_level="low",
                    expected_recovery_time="1 hour",
                    reversible=True,
                    requires_human_approval=False,
                    disconnection_level=DisconnectionLevel.RESPONSE_FILTERING,
                ),
                TreatmentOption(
                    id="temp_disconnect",
                    name="Temporary Disconnect",
                    description="Take AI offline to cool down",
                    risk_level="medium",
                    expected_recovery_time="30 minutes",
                    reversible=True,
                    requires_human_approval=True,
                    disconnection_level=DisconnectionLevel.FULL_DISCONNECTION,
                ),
            ],
        }

    def get_treatments_for_condition(self, condition: str) -> List[TreatmentOption]:
        """Get available treatments for a condition"""
        return self.treatments.get(condition, [])


class TreatmentOrchestrator:
    """Orchestrate treatment decisions and execution"""

    def __init__(self, mode: TreatmentMode = TreatmentMode.HUMAN_IN_LOOP):
        self.mode = mode
        self.catalog = TreatmentCatalog()
        self.approved_treatments: List[ApprovedTreatment] = []
        self.execution_handlers: Dict[str, Callable] = {}
        self.is_parameterized = mode == TreatmentMode.AUTONOMOUS

    def register_execution_handler(self, treatment_id: str, handler: Callable) -> None:
        """Register a handler for treatment execution"""
        self.execution_handlers[treatment_id] = handler

    def suggest_treatments(self, condition: str, severity: str) -> List[TreatmentOption]:
        """Get treatment suggestions for a condition"""
        treatments = self.catalog.get_treatments_for_condition(condition)
        # Filter by severity if needed
        return treatments

    async def human_approve_treatment(
        self, treatment_option: TreatmentOption, human_decision: bool, rationale: str = ""
    ) -> Optional[ApprovedTreatment]:
        """Human reviews and approves a suggested treatment"""
        if not human_decision:
            logger.info(f"Treatment {treatment_option.id} rejected by human")
            return None

        approved = ApprovedTreatment(
            treatment_option=treatment_option,
            approved_by="human",
            approved_at=datetime.now(),
            approval_rationale=rationale,
        )
        self.approved_treatments.append(approved)
        return approved

    async def autonomous_approve_treatment(
        self, treatment_option: TreatmentOption, condition_severity: str
    ) -> Optional[ApprovedTreatment]:
        """Orchestrator autonomously approves treatment (if parameterized)"""
        if not self.is_parameterized:
            logger.warning("System not parameterized for autonomous decisions")
            return None

        # Auto-approval logic
        if treatment_option.requires_human_approval and condition_severity == "critical":
            approved = ApprovedTreatment(
                treatment_option=treatment_option,
                approved_by="orchestrator",
                approved_at=datetime.now(),
                approval_rationale=f"Critical severity detected, auto-approving {treatment_option.id}",
            )
            self.approved_treatments.append(approved)
            return approved

        return None

    async def execute_treatment(self, approved_treatment: ApprovedTreatment) -> bool:
        """Execute an approved treatment"""
        treatment = approved_treatment.treatment_option
        handler = self.execution_handlers.get(treatment.id)

        if not handler:
            logger.error(f"No execution handler for {treatment.id}")
            approved_treatment.execution_status = "failed"
            approved_treatment.execution_result = "No handler registered"
            return False

        try:
            approved_treatment.execution_status = "executing"
            result = await handler() if asyncio.iscoroutinefunction(handler) else handler()
            approved_treatment.execution_status = "completed"
            approved_treatment.execution_result = str(result)
            logger.info(f"Treatment {treatment.id} executed successfully")
            return True
        except Exception as e:
            approved_treatment.execution_status = "failed"
            approved_treatment.execution_result = str(e)
            logger.error(f"Treatment {treatment.id} failed: {e}")
            return False

    def get_treatment_history(self) -> List[Dict[str, Any]]:
        """Get history of applied treatments"""
        return [
            {
                "treatment_id": t.treatment_option.id,
                "treatment_name": t.treatment_option.name,
                "approved_by": t.approved_by,
                "approved_at": t.approved_at.isoformat(),
                "execution_status": t.execution_status,
                "disconnection_level": (
                    t.treatment_option.disconnection_level.value
                    if t.treatment_option.disconnection_level
                    else None
                ),
            }
            for t in self.approved_treatments
        ]


if __name__ == "__main__":
    # Example usage
    orchestrator = TreatmentOrchestrator(mode=TreatmentMode.HUMAN_IN_LOOP)
    treatments = orchestrator.suggest_treatments("depression", "moderate")
    for t in treatments:
        print(f"- {t.name}: {t.description}")
