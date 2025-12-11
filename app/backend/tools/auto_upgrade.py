"""Auto-Upgrade Module - Intelligent Package Upgrades with Validation

Automatically detects outdated packages, validates compatibility,
and upgrades them responsibly while maintaining system health.
"""

import subprocess
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class PackageManager:
    """Manage package updates and version constraints"""

    def __init__(self, requirements_file: Path = Path("requirements.txt")):
        self.requirements_file = requirements_file
        self.packages = {}
        self.load_requirements()

    def load_requirements(self) -> Dict[str, str]:
        """Load packages and versions from requirements.txt"""
        if not self.requirements_file.exists():
            logger.warning(f"Requirements file not found: {self.requirements_file}")
            return {}

        self.packages = {}
        with open(self.requirements_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse package name and version
                    match = re.match(r"([a-zA-Z0-9_-]+)([~=><]*)(.*)", line)
                    if match:
                        pkg_name, operator, version = match.groups()
                        self.packages[pkg_name.lower()] = {
                            "name": pkg_name,
                            "operator": operator or "~=",
                            "version": version.strip(),
                            "original": line,
                        }
        return self.packages

    def get_outdated_packages(self) -> List[Dict[str, Any]]:
        """Find outdated packages (simulated)"""
        # In production, run: pip list --outdated --format json
        outdated = []
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                outdated = [
                    {
                        "name": pkg["name"],
                        "current": pkg["version"],
                        "latest": pkg["latest_version"],
                    }
                    for pkg in data
                ]
        except Exception as e:
            logger.error(f"Failed to get outdated packages: {e}")
        return outdated

    def validate_upgrade_safe(self, package_name: str, new_version: str) -> bool:
        """Check if upgrade is safe (major version changes detected)"""
        # Extract major versions
        def get_major_version(version_str: str) -> str:
            return version_str.split(".")[0]

        if package_name.lower() not in self.packages:
            return True  # New package, safe to add

        current = self.packages[package_name.lower()]["version"]
        current_major = get_major_version(current)
        new_major = get_major_version(new_version)

        # Don't allow major version changes automatically
        if current_major != new_major:
            logger.warning(
                f"Major version change for {package_name}: {current} -> {new_version} (blocked)"
            )
            return False

        return True

    def update_requirement(self, package_name: str, new_version: str) -> bool:
        """Update a package version in requirements.txt"""
        if not self.validate_upgrade_safe(package_name, new_version):
            return False

        try:
            # Read current requirements
            with open(self.requirements_file) as f:
                lines = f.readlines()

            # Find and update the package
            updated = False
            new_lines = []
            for line in lines:
                if line.strip().startswith(package_name.lower()):
                    new_lines.append(f"{package_name}~={new_version}\n")
                    updated = True
                else:
                    new_lines.append(line)

            if updated:
                with open(self.requirements_file, "w") as f:
                    f.writelines(new_lines)
                logger.info(f"Updated {package_name} to {new_version}")
                return True
        except Exception as e:
            logger.error(f"Failed to update {package_name}: {e}")
            return False


class AutoUpgradeOrchestrator:
    """Orchestrate safe, automated package upgrades"""

    def __init__(self, requirements_file: Path = Path("requirements.txt")):
        self.package_mgr = PackageManager(requirements_file)
        self.upgrade_history = []

    def perform_safe_upgrades(self, dry_run: bool = True) -> Dict[str, Any]:
        """Perform safe minor/patch version upgrades"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "outdated_found": [],
            "upgraded": [],
            "skipped": [],
            "errors": [],
        }

        outdated = self.package_mgr.get_outdated_packages()
        report["outdated_found"] = [pkg["name"] for pkg in outdated]

        for pkg in outdated:
            is_safe = self.package_mgr.validate_upgrade_safe(pkg["name"], pkg["latest"])
            if is_safe:
                if not dry_run:
                    success = self.package_mgr.update_requirement(pkg["name"], pkg["latest"])
                    if success:
                        report["upgraded"].append(pkg["name"])
                    else:
                        report["errors"].append(f"Failed to upgrade {pkg['name']}")
                else:
                    report["upgraded"].append(f"{pkg['name']} (would upgrade)")
            else:
                report["skipped"].append(
                    f"{pkg['name']}: major version change blocked"
                )

        self.upgrade_history.append(report)
        return report

    def check_dependency_conflicts(self) -> List[str]:
        """Check for potential dependency conflicts"""
        conflicts = []
        try:
            # Run pip check to detect conflicts
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                conflicts.append(result.stdout)
        except Exception as e:
            conflicts.append(f"Failed to check dependencies: {e}")
        return conflicts

    def generate_upgrade_report(self, dry_run: bool = True) -> Dict[str, Any]:
        """Generate comprehensive upgrade report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "upgrade_status": self.perform_safe_upgrades(dry_run=dry_run),
            "dependency_conflicts": self.check_dependency_conflicts(),
            "recommendation": "Safe to apply upgrades" if not self.check_dependency_conflicts() else "Review conflicts before upgrading",
        }


if __name__ == "__main__":
    orchestrator = AutoUpgradeOrchestrator()
    # Perform dry-run first
    report = orchestrator.generate_upgrade_report(dry_run=True)
    print(json.dumps(report, indent=2, default=str))
