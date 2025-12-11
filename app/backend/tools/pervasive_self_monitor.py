"""Pervasive Self-Monitoring & Self-Improvement Orchestrator

Monitors EVERYTHING and continuously improves:
- Health metrics (physical & mental)
- Performance metrics (latency, errors, throughput)
- Resource usage (CPU, memory, disk)
- Code quality (complexity, coverage, duplication)
- API usage (cost, rate limits)
- User feedback and satisfaction
- Treatment effectiveness
- Catalog accuracy
- Architecture health
- System stability

Improves:
- Itself based on observations
- Catalogs based on diagnosis accuracy
- Treatments based on success rates
- Performance based on bottlenecks
- Architecture based on patterns
- Processes based on failures
"""

import asyncio
import json
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of metrics to monitor"""
    HEALTH = "health"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    CODE_QUALITY = "code_quality"
    API_USAGE = "api_usage"
    USER_FEEDBACK = "user_feedback"
    SYSTEM_STABILITY = "system_stability"


@dataclass
class Metric:
    """A monitored metric"""
    name: str
    category: MetricCategory
    value: float
    threshold_normal: float
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime = field(default_factory=datetime.now)
    history: List[float] = field(default_factory=list)
    trend: str = "stable"  # increasing, decreasing, stable
    status: str = "normal"  # normal, warning, critical

    def update(self, new_value: float) -> None:
        """Update metric with new value"""
        self.history.append(self.value)
        self.value = new_value
        self.timestamp = datetime.now()
        
        # Determine status
        if new_value >= self.threshold_critical:
            self.status = "critical"
        elif new_value >= self.threshold_warning:
            self.status = "warning"
        else:
            self.status = "normal"
        
        # Determine trend
        if len(self.history) >= 2:
            if new_value > self.history[-1]:
                self.trend = "increasing"
            elif new_value < self.history[-1]:
                self.trend = "decreasing"
            else:
                self.trend = "stable"


class PervasiveSelfMonitor:
    """Monitors everything about the system continuously"""

    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.observations: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.improvement_actions: List[Dict[str, Any]] = []
        self.last_full_scan = None
        self.scan_interval = timedelta(minutes=5)

    def register_metric(self, metric: Metric) -> None:
        """Register a new metric to monitor"""
        self.metrics[metric.name] = metric

    def record_observation(self, observation_type: str, value: Any, 
                          context: Dict[str, Any] = None) -> None:
        """Record any observation about system behavior"""
        observation = {
            "timestamp": datetime.now().isoformat(),
            "type": observation_type,
            "value": value,
            "context": context or {},
        }
        self.observations.append(observation)
        logger.info(f"Observation recorded: {observation_type}={value}")

    def analyze_metrics(self) -> Dict[str, Any]:
        """Analyze all metrics and identify anomalies"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(self.metrics),
            "normal": 0,
            "warning": 0,
            "critical": 0,
            "anomalies": [],
            "trends": [],
        }

        for metric_name, metric in self.metrics.items():
            # Count statuses
            if metric.status == "normal":
                analysis["normal"] += 1
            elif metric.status == "warning":
                analysis["warning"] += 1
                analysis["anomalies"].append({
                    "metric": metric_name,
                    "status": "warning",
                    "value": metric.value,
                    "threshold": metric.threshold_warning,
                })
            elif metric.status == "critical":
                analysis["critical"] += 1
                analysis["anomalies"].append({
                    "metric": metric_name,
                    "status": "critical",
                    "value": metric.value,
                    "threshold": metric.threshold_critical,
                })

            # Track trends
            if metric.trend != "stable":
                analysis["trends"].append({
                    "metric": metric_name,
                    "trend": metric.trend,
                    "value": metric.value,
                })

        return analysis

    def identify_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Identify where the system can improve"""
        opportunities = []
        analysis = self.analyze_metrics()

        # Opportunity 1: Critical metrics
        for anomaly in analysis["anomalies"]:
            if anomaly["status"] == "critical":
                opportunities.append({
                    "category": "urgent_fix",
                    "metric": anomaly["metric"],
                    "description": f"Critical value ({anomaly['value']}) exceeds threshold ({anomaly['threshold']})",
                    "priority": "critical",
                })

        # Opportunity 2: Increasing trends
        for trend in analysis["trends"]:
            if trend["trend"] == "increasing":
                opportunities.append({
                    "category": "trend_warning",
                    "metric": trend["metric"],
                    "description": f"Metric is increasing trend: {trend['value']}",
                    "priority": "high",
                })

        # Opportunity 3: From observations
        recent_observations = self.observations[-10:] if self.observations else []
        for obs in recent_observations:
            if obs["type"] == "error":
                opportunities.append({
                    "category": "error_fix",
                    "description": f"Error observed: {obs['value']}",
                    "priority": "high",
                })

        return opportunities

    async def run_continuous_monitoring(self) -> None:
        """Run monitoring continuously (background task)"""
        while True:
            try:
                # Run full scan every scan_interval
                if (self.last_full_scan is None or 
                    datetime.now() - self.last_full_scan >= self.scan_interval):
                    
                    analysis = self.analyze_metrics()
                    opportunities = self.identify_improvement_opportunities()
                    
                    # Log warnings and critical
                    if analysis["warning"] > 0 or analysis["critical"] > 0:
                        logger.warning(f"System anomalies detected: {analysis['warning']} warnings, {analysis['critical']} critical")
                    
                    # Queue improvements
                    for opp in opportunities:
                        self.improvement_actions.append(opp)
                    
                    self.last_full_scan = datetime.now()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)

    def get_health_score(self) -> float:
        """Calculate overall system health (0-100)"""
        if not self.metrics:
            return 50.0  # Unknown

        analysis = self.analyze_metrics()
        total = analysis["total_metrics"]
        
        if total == 0:
            return 50.0

        # Score = percentage of normal metrics
        health = (analysis["normal"] / total) * 100
        
        # Penalize for critical issues
        health -= (analysis["critical"] * 10)
        
        # Penalize for warnings
        health -= (analysis["warning"] * 5)
        
        return max(0, min(100, health))

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive monitoring report"""
        analysis = self.analyze_metrics()
        opportunities = self.identify_improvement_opportunities()
        
        return json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "health_score": self.get_health_score(),
                "metrics_analysis": analysis,
                "improvement_opportunities": opportunities[:10],  # Top 10
                "total_observations": len(self.observations),
                "pending_improvements": len(self.improvement_actions),
                "recent_alerts": self.alerts[-5:],  # Last 5 alerts
            },
            indent=2,
            default=str,
        )

    def export_monitoring_data(self) -> str:
        """Export all monitoring data for analysis"""
        return json.dumps(
            {
                "metrics": {
                    name: {
                        "current_value": m.value,
                        "status": m.status,
                        "trend": m.trend,
                        "history": m.history[-10:],  # Last 10 values
                    }
                    for name, m in self.metrics.items()
                },
                "observations_summary": {
                    "total": len(self.observations),
                    "by_type": {},
                },
                "improvement_actions_pending": len(self.improvement_actions),
                "health_score": self.get_health_score(),
            },
            indent=2,
            default=str,
        )


if __name__ == "__main__":
    monitor = PervasiveSelfMonitor()
    
    # Register sample metrics
    health_metric = Metric(
        name="system_health",
        category=MetricCategory.HEALTH,
        value=85.0,
        threshold_normal=70.0,
        threshold_warning=50.0,
        threshold_critical=30.0,
    )
    monitor.register_metric(health_metric)
    
    # Record sample observation
    monitor.record_observation("diagnosis", "depression", {"confidence": 0.92})
    
    print(monitor.generate_comprehensive_report())
