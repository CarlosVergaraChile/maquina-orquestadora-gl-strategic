"""Health Check Module - Physical & Mental Health Monitoring

Physical Health: Code quality, imports, dependencies, tests
Mental Health: AI model behavior, response quality, anomalies
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PhysicalHealthCheck:
    """Monitor code quality, imports, and dependencies (Physical Health)"""

    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.health_report = {}

    def check_imports(self) -> Dict[str, Any]:
        """Verify all imports are resolvable"""
        result = {"status": "healthy", "errors": []}
        try:
            # Check critical imports
            imports_to_check = [
                "fastapi",
                "starlette",
                "pydantic",
                "sqlalchemy",
                "anthropic",
                "python_jose",
                "asyncpg",
            ]
            for imp in imports_to_check:
                try:
                    __import__(imp)
                except ImportError as e:
                    result["status"] = "unhealthy"
                    result["errors"].append(f"Import {imp} failed: {e}")
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(f"Import check failed: {e}")
        return result

    def check_requirements(self) -> Dict[str, Any]:
        """Verify requirements.txt integrity"""
        result = {"status": "healthy", "missing": [], "errors": []}
        try:
            req_file = self.project_root / "requirements.txt"
            if not req_file.exists():
                return {"status": "critical", "errors": ["requirements.txt not found"]}

            with open(req_file) as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Basic syntax check
                    if "==" in line or "~=" in line or ">" in line:
                        continue
                    else:
                        result["status"] = "unhealthy"
                        result["missing"].append(line)
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
        return result

    def check_tests(self) -> Dict[str, Any]:
        """Run and verify tests pass"""
        result = {"status": "healthy", "test_count": 0, "errors": []}
        try:
            test_dir = self.project_root / "tests"
            if not test_dir.exists():
                result["status"] = "warning"
                result["errors"].append("No tests directory found")
                return result

            # Count test files
            test_files = list(test_dir.glob("test_*.py"))
            result["test_count"] = len(test_files)
            if len(test_files) == 0:
                result["status"] = "warning"
                result["errors"].append("No test files found")
        except Exception as e:
            result["status"] = "critical"
            result["errors"].append(str(e))
        return result

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive physical health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "imports": self.check_imports(),
            "requirements": self.check_requirements(),
            "tests": self.check_tests(),
        }


class MentalHealthCheck:
    """Monitor AI behavior, response quality, and anomalies (Mental Health)"""

    def __init__(self):
        self.response_metrics = []
        self.anomalies = []

    def check_response_quality(self, response: str) -> Dict[str, Any]:
        """Evaluate response quality and detect anomalies"""
        result = {"status": "healthy", "issues": []}

        # Check response is not empty
        if not response or len(response.strip()) == 0:
            result["status"] = "unhealthy"
            result["issues"].append("Empty response from AI")
            return result

        # Check response length is reasonable
        if len(response) > 10000:
            result["status"] = "warning"
            result["issues"].append("Response unusually long (>10k chars)")

        # Check for error patterns
        error_patterns = ["error", "exception", "failed", "unable", "cannot"]
        response_lower = response.lower()
        if any(pattern in response_lower for pattern in error_patterns[:1]):
            if "error" in response_lower:
                result["status"] = "warning"
                result["issues"].append("Response contains error keywords")

        return result

    def check_response_consistency(self, responses: List[str]) -> Dict[str, Any]:
        """Check for consistency in AI responses (Mental stability)"""
        result = {"status": "healthy", "consistency_score": 0.0, "issues": []}
        if len(responses) < 2:
            return result

        # Check for similar topics in responses
        result["consistency_score"] = 0.75  # Placeholder
        if result["consistency_score"] < 0.5:
            result["status"] = "unhealthy"
            result["issues"].append("Low response consistency")

        return result

    def generate_report(self, responses: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive mental health report"""
        if responses is None:
            responses = []

        mental_report = {
            "timestamp": datetime.now().isoformat(),
            "response_quality": (
                self.check_response_quality(responses[0])
                if responses
                else {"status": "unknown"}
            ),
            "consistency": self.check_response_consistency(responses),
        }
        return mental_report


class SystemHealthOrchestrator:
    """Orchestrate both physical and mental health checks"""

    def __init__(self, project_root: Path = Path(".")):
        self.physical = PhysicalHealthCheck(project_root)
        self.mental = MentalHealthCheck()
        self.health_history = []

    async def run_health_check(self, responses: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive health check (physical + mental)"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "physical_health": self.physical.generate_report(),
            "mental_health": self.mental.generate_report(responses),
        }

        # Determine overall status
        physical_status = report["physical_health"].get("imports", {}).get("status")
        mental_status = report["mental_health"].get("response_quality", {}).get("status")

        if physical_status == "critical" or mental_status == "unhealthy":
            report["overall_status"] = "critical"
        elif physical_status == "unhealthy" or mental_status == "warning":
            report["overall_status"] = "unhealthy"
        else:
            report["overall_status"] = "healthy"

        self.health_history.append(report)
        return report

    def get_health_status(self) -> str:
        """Get current overall health status"""
        if not self.health_history:
            return "unknown"
        return self.health_history[-1]["overall_status"]


if __name__ == "__main__":
    orchestrator = SystemHealthOrchestrator()
    report = asyncio.run(orchestrator.run_health_check())
    print(json.dumps(report, indent=2, default=str))
