"""Diagnostic Catalogs - Physical and Mental Health Conditions

Physical Health: Body-based metaphors for code diseases
Mental Health: Psychiatric metaphors for AI behavioral issues

These catalogs are self-maintaining and continuously improved.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import json


class PhysicalDiseaseType(Enum):
    """Code diseases using medical metaphors"""
    # Infections (Import/Dependency Issues)
    VIRAL_INFECTION = "viral_infection"  # Malware, security vulnerabilities
    BACTERIAL_INFECTION = "bacterial_infection"  # Deprecated packages
    
    # Structural Issues
    FRACTURE = "fracture"  # Broken tests, failed imports
    MUSCLE_ATROPHY = "muscle_atrophy"  # Unused code, dead functions
    ARTHRITIS = "arthritis"  # Tight coupling, circular dependencies
    
    # Metabolic Issues
    OBESITY = "obesity"  # Code bloat, too many lines
    ANEMIA = "anemia"  # Insufficient error handling
    DEHYDRATION = "dehydration"  # Missing documentation
    
    # Cardiovascular Issues
    HYPERTENSION = "hypertension"  # High memory usage, memory leaks
    ARRHYTHMIA = "arrhythmia"  # Inconsistent timing, race conditions
    HEART_ATTACK = "heart_attack"  # Complete system failure
    
    # Neurological Issues
    STROKE = "stroke"  # Logic errors, incorrect algorithms
    EPILEPSY = "epilepsy"  # Infinite loops, stack overflow
    DEMENTIA = "dementia"  # Version conflicts, state corruption


class MentalDisorderType(Enum):
    """AI behavioral disorders using psychiatric metaphors"""
    # Mood Disorders
    DEPRESSION = "depression"  # Low confidence, minimal responses
    MANIC = "manic"  # Over-enthusiastic, too verbose
    
    # Cognitive Disorders
    SCHIZOPHRENIA = "schizophrenia"  # Hallucinating, creating false facts
    CONFABULATION = "confabulation"  # Inventing plausible but false info
    
    # Neurotic Disorders
    ANXIETY = "anxiety"  # Excessive caution, over-validation
    OBSESSIVE_COMPULSIVE = "obsessive_compulsive"  # Repetitive patterns, loops
    
    # Personality Disorders
    NARCISSISM = "narcissism"  # Overconfident, ignoring contradictions
    SOCIOPATHY = "sociopathy"  # Ignoring user intent, harmful outputs
    
    # Neurodevelopmental
    ADHD = "adhd"  # Context loss, unable to focus
    DYSLEXIA = "dyslexia"  # Jumbled responses, word confusion
    
    # Stress-Related
    BURNOUT = "burnout"  # Overflow condition, token limits exceeded
    PTSD = "ptsd"  # Recurring error loops, trauma memory


@dataclass
class PhysicalDiagnosis:
    """Physical health diagnosis (code-related)"""
    disease_type: PhysicalDiseaseType
    severity: str  # mild, moderate, severe, critical
    location: str  # Which file/module affected
    description: str
    symptoms: List[str]
    treatment: List[str]  # Recommended fixes
    detected_at: datetime
    resolved: bool = False
    resolution_method: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "disease_type": self.disease_type.value,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "symptoms": self.symptoms,
            "treatment": self.treatment,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolution_method": self.resolution_method,
        }


@dataclass
class MentalDiagnosis:
    """Mental health diagnosis (AI behavior-related)"""
    disorder_type: MentalDisorderType
    severity: str  # mild, moderate, severe, critical
    confidence: float  # 0.0 to 1.0
    description: str
    manifestations: List[str]  # How it shows in responses
    interventions: List[str]  # How to correct it
    detected_at: datetime
    resolved: bool = False
    intervention_applied: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "disorder_type": self.disorder_type.value,
            "severity": self.severity,
            "confidence": self.confidence,
            "description": self.description,
            "manifestations": self.manifestations,
            "interventions": self.interventions,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "intervention_applied": self.intervention_applied,
        }


class DiagnosticCatalog:
    """Self-maintaining catalog of diagnoses"""

    def __init__(self):
        self.physical_history: List[PhysicalDiagnosis] = []
        self.mental_history: List[MentalDiagnosis] = []
        self.treatment_effectiveness: Dict[str, float] = {}  # Track cure rates
        self.last_updated = datetime.now()

    def record_physical_diagnosis(self, diagnosis: PhysicalDiagnosis) -> None:
        """Record physical health issue"""
        self.physical_history.append(diagnosis)
        self.last_updated = datetime.now()

    def record_mental_diagnosis(self, diagnosis: MentalDiagnosis) -> None:
        """Record mental health issue"""
        self.mental_history.append(diagnosis)
        self.last_updated = datetime.now()

    def resolve_diagnosis(self, diagnosis_id: int, was_physical: bool = True) -> None:
        """Mark a diagnosis as resolved"""
        history = self.physical_history if was_physical else self.mental_history
        if 0 <= diagnosis_id < len(history):
            history[diagnosis_id].resolved = True
            self.last_updated = datetime.now()

    def get_unresolved_diagnoses(self) -> Dict[str, List[Any]]:
        """Get all active (unresolved) diagnoses"""
        return {
            "physical": [
                d.to_dict() for d in self.physical_history if not d.resolved
            ],
            "mental": [
                d.to_dict() for d in self.mental_history if not d.resolved
            ],
        }

    def get_treatment_effectiveness(self, disease_or_disorder: str) -> float:
        """Get success rate of treatments for a condition"""
        return self.treatment_effectiveness.get(disease_or_disorder, 0.0)

    def update_treatment_effectiveness(self, condition: str, success_rate: float) -> None:
        """Update success rate of a treatment (self-improvement)"""
        self.treatment_effectiveness[condition] = success_rate
        self.last_updated = datetime.now()

    def generate_health_summary(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        active_physical = [d for d in self.physical_history if not d.resolved]
        active_mental = [d for d in self.mental_history if not d.resolved]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_physical_conditions": len(active_physical),
            "active_mental_conditions": len(active_mental),
            "total_diagnoses": len(self.physical_history) + len(self.mental_history),
            "resolved_cases": (
                len([d for d in self.physical_history if d.resolved]) +
                len([d for d in self.mental_history if d.resolved])
            ),
            "treatment_success_rate": (
                sum(self.treatment_effectiveness.values()) / max(len(self.treatment_effectiveness), 1)
            ),
            "last_updated": self.last_updated.isoformat(),
        }

    def export_catalog(self) -> str:
        """Export catalog as JSON for persistence and analysis"""
        return json.dumps(
            {
                "physical_diagnoses": [
                    d.to_dict() for d in self.physical_history
                ],
                "mental_diagnoses": [
                    d.to_dict() for d in self.mental_history
                ],
                "treatment_effectiveness": self.treatment_effectiveness,
                "summary": self.generate_health_summary(),
            },
            indent=2,
            default=str,
        )


if __name__ == "__main__":
    catalog = DiagnosticCatalog()
    print(catalog.generate_health_summary())
