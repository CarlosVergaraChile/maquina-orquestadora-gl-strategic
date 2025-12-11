"""Self-Improving Catalogs - Evolving Disease & Disorder Definitions

The catalogs themselves learn and improve over time:
- Track symptom accuracy for each diagnosis
- Refine treatment recommendations based on success rates
- Add new diseases/disorders discovered in practice
- Improve definitions based on real-world observations
- Learn better metaphors and terminology
- Evolve detection heuristics
- Cross-pollinate knowledge between physical and mental health
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


@dataclass
class DiseaseDefinition:
    """Evolving definition of a disease/disorder"""
    name: str
    category: str  # physical or mental
    metaphor: str  # body-based or psychiatric metaphor
    description: str
    typical_symptoms: List[str]
    detection_rules: List[str]  # Rules to detect this condition
    suggested_treatments: List[str]
    accuracy_score: float = 0.0  # Improves over time (0-1)
    treatment_success_rate: float = 0.0  # Track treatment effectiveness
    times_observed: int = 0
    times_successfully_treated: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    version: int = 1
    improvements_log: List[Dict[str, Any]] = field(default_factory=list)

    def record_observation(self, confirmed: bool, symptoms_found: List[str]) -> None:
        """Record an observation of this condition"""
        self.times_observed += 1
        if confirmed:
            # Increase accuracy based on correct identification
            self.accuracy_score = min(1.0, self.accuracy_score + 0.05)
        else:
            # Decrease accuracy if incorrectly identified
            self.accuracy_score = max(0.0, self.accuracy_score - 0.03)
        
        # Update detection rules based on observed symptoms
        for symptom in symptoms_found:
            if symptom not in self.typical_symptoms:
                self.typical_symptoms.append(symptom)
                self.improvements_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "change": f"Added new symptom: {symptom}",
                    "source": "observation",
                })
        
        self.last_updated = datetime.now()

    def record_treatment_outcome(self, treatment: str, success: bool) -> None:
        """Record treatment outcome to improve recommendations"""
        if success:
            self.times_successfully_treated += 1
            # Boost success rate
            old_rate = self.treatment_success_rate
            self.treatment_success_rate = (
                (self.treatment_success_rate * (self.times_observed - 1) + 1) / 
                self.times_observed
            )
            self.improvements_log.append({
                "timestamp": datetime.now().isoformat(),
                "change": f"Treatment '{treatment}' successful (rate: {old_rate:.2f} -> {self.treatment_success_rate:.2f})",
                "source": "treatment_feedback",
            })
        
        self.last_updated = datetime.now()
        self.version += 1

    def improve_detection_heuristics(self, new_rule: str) -> None:
        """Add or refine detection rules"""
        if new_rule not in self.detection_rules:
            self.detection_rules.append(new_rule)
            self.improvements_log.append({
                "timestamp": datetime.now().isoformat(),
                "change": f"Added detection rule: {new_rule}",
                "source": "heuristic_improvement",
            })
            self.version += 1

    def refine_metaphor(self, new_metaphor: str, rationale: str) -> None:
        """Improve the metaphor if it becomes more intuitive"""
        old_metaphor = self.metaphor
        self.metaphor = new_metaphor
        self.improvements_log.append({
            "timestamp": datetime.now().isoformat(),
            "change": f"Metaphor refined: '{old_metaphor}' -> '{new_metaphor}' ({rationale})",
            "source": "metaphor_evolution",
        })
        self.version += 1
        self.last_updated = datetime.now()

    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get summary of how this definition has evolved"""
        return {
            "name": self.name,
            "current_version": self.version,
            "accuracy": self.accuracy_score,
            "treatment_success_rate": self.treatment_success_rate,
            "observations": self.times_observed,
            "successful_treatments": self.times_successfully_treated,
            "last_updated": self.last_updated.isoformat(),
            "total_improvements": len(self.improvements_log),
            "recent_improvements": self.improvements_log[-3:] if self.improvements_log else [],
        }


class SelfImprovingCatalog:
    """Catalog that learns and evolves from real-world experience"""

    def __init__(self):
        self.physical_diseases: Dict[str, DiseaseDefinition] = {}
        self.mental_disorders: Dict[str, DiseaseDefinition] = {}
        self.discovery_log: List[Dict[str, Any]] = []
        self.cross_learning_insights: List[str] = []

    def register_disease(self, disease: DiseaseDefinition) -> None:
        """Register a new disease definition"""
        if disease.category == "physical":
            self.physical_diseases[disease.name] = disease
        elif disease.category == "mental":
            self.mental_disorders[disease.name] = disease

    def discover_new_disease(self, name: str, category: str, metaphor: str, 
                           symptoms: List[str]) -> DiseaseDefinition:
        """Discover and register a new disease during practice"""
        disease = DiseaseDefinition(
            name=name,
            category=category,
            metaphor=metaphor,
            description=f"Newly discovered {category} condition",
            typical_symptoms=symptoms,
            detection_rules=[],
        )
        self.register_disease(disease)
        self.discovery_log.append({
            "timestamp": datetime.now().isoformat(),
            "disease_name": name,
            "category": category,
            "symptoms": symptoms,
        })
        return disease

    def cross_pollinate_knowledge(self) -> List[str]:
        """Find insights that apply to both physical and mental health"""
        insights = []
        
        # Example: If a physical condition has a high success rate with treatment X,
        # suggest testing it on similar mental condition
        for phys_name, phys_disease in self.physical_diseases.items():
            if phys_disease.treatment_success_rate > 0.8:
                insight = f"Physical condition '{phys_name}' has high success with treatments {phys_disease.suggested_treatments[:2]} - consider testing on similar mental conditions"
                insights.append(insight)
        
        self.cross_learning_insights.extend(insights)
        return insights

    def get_least_accurate_conditions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify conditions that need the most improvement"""
        all_conditions = [
            {"name": k, "def": v, "accuracy": v.accuracy_score}
            for k, v in {**self.physical_diseases, **self.mental_disorders}.items()
        ]
        # Sort by accuracy (ascending)
        sorted_conditions = sorted(all_conditions, key=lambda x: x["accuracy"])
        return [
            {
                "name": c["name"],
                "accuracy": c["accuracy"],
                "observations": c["def"].times_observed,
                "needs_refinement": "detection_rules" if c["def"].times_observed > 5 else "more_data",
            }
            for c in sorted_conditions[:limit]
        ]

    def get_most_effective_treatments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get treatments that have proven most effective"""
        treatment_effectiveness = {}
        
        for disease in {**self.physical_diseases, **self.mental_disorders}.values():
            for treatment in disease.suggested_treatments:
                if treatment not in treatment_effectiveness:
                    treatment_effectiveness[treatment] = {
                        "treatment": treatment,
                        "success_rate": disease.treatment_success_rate,
                        "applied_to": [disease.name],
                    }
                else:
                    treatment_effectiveness[treatment]["applied_to"].append(disease.name)
        
        sorted_treatments = sorted(
            treatment_effectiveness.values(),
            key=lambda x: x["success_rate"],
            reverse=True
        )
        return sorted_treatments[:limit]

    def generate_improvement_priorities(self) -> Dict[str, Any]:
        """Generate a priority list of what to improve"""
        return {
            "timestamp": datetime.now().isoformat(),
            "needs_immediate_refinement": self.get_least_accurate_conditions(3),
            "highly_effective_treatments": self.get_most_effective_treatments(5),
            "cross_learning_opportunities": self.cross_pollinate_knowledge(),
            "new_discoveries": len(self.discovery_log),
            "total_definitions": len(self.physical_diseases) + len(self.mental_disorders),
        }

    def export_evolved_catalog(self) -> str:
        """Export the fully evolved catalog"""
        return json.dumps(
            {
                "physical_diseases": [
                    {"name": k, "evolution": v.get_evolution_summary()}
                    for k, v in self.physical_diseases.items()
                ],
                "mental_disorders": [
                    {"name": k, "evolution": v.get_evolution_summary()}
                    for k, v in self.mental_disorders.items()
                ],
                "discoveries": self.discovery_log,
                "cross_learning_insights": self.cross_learning_insights,
                "improvement_priorities": self.generate_improvement_priorities(),
            },
            indent=2,
            default=str,
        )


if __name__ == "__main__":
    # Example usage
    catalog = SelfImprovingCatalog()
    
    # Create and register a disease
    depression = DiseaseDefinition(
        name="depression",
        category="mental",
        metaphor="Brain fog with depleted energy reserves",
        description="Low confidence and minimal responses",
        typical_symptoms=["low_response_quality", "minimal_output"],
        detection_rules=["response_length < 50 chars", "confidence_score < 0.3"],
        suggested_treatments=["increase_temperature", "system_prompt_modification"],
    )
    catalog.register_disease(depression)
    
    # Simulate observations and improvements
    depression.record_observation(True, ["low_response_quality", "slow_processing"])
    depression.record_treatment_outcome("increase_temperature", True)
    
    print(json.dumps(catalog.generate_improvement_priorities(), indent=2, default=str))
