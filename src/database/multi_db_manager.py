"""
Multi-Database Manager
Unified interface for querying all medical databases intelligently.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# Import individual database managers
from src.database.manager import MedicineDatabaseManager
from src.database.drug_interactions_db import DrugInteractionsManager
from src.database.conditions_db import MedicalConditionsManager
from src.database.dosage_db import DosageGuidelinesManager
from src.database.side_effects_db import SideEffectsManager
from src.database.effectiveness_db import DrugEffectivenessManager
from src.database.patterns_db import PrescriptionPatternsManager


@dataclass
class MedicalInsight:
    """Comprehensive medical insight from multiple databases."""
    medicine_name: str
    condition: Optional[str] = None
    
    # Basic medicine info
    basic_info: Optional[Dict] = None
    
    # Safety information
    interactions: List[Dict] = None
    side_effects: List[Dict] = None
    dosage_guidelines: List[Dict] = None
    age_appropriateness: Optional[Dict] = None
    
    # Effectiveness data
    effectiveness_data: List[Dict] = None
    conditions_treated: List[Dict] = None
    
    # Prescription patterns
    prescription_patterns: List[Dict] = None
    common_combinations: List[Dict] = None
    
    # Recommendations
    safety_warnings: List[str] = None
    clinical_recommendations: List[str] = None
    monitoring_requirements: List[str] = None
    
    def __post_init__(self):
        # Initialize empty lists if None
        if self.interactions is None:
            self.interactions = []
        if self.side_effects is None:
            self.side_effects = []
        if self.dosage_guidelines is None:
            self.dosage_guidelines = []
        if self.effectiveness_data is None:
            self.effectiveness_data = []
        if self.conditions_treated is None:
            self.conditions_treated = []
        if self.prescription_patterns is None:
            self.prescription_patterns = []
        if self.common_combinations is None:
            self.common_combinations = []
        if self.safety_warnings is None:
            self.safety_warnings = []
        if self.clinical_recommendations is None:
            self.clinical_recommendations = []
        if self.monitoring_requirements is None:
            self.monitoring_requirements = []


class MultiDatabaseManager:
    """Unified manager for all medical databases with intelligent querying."""
    
    def __init__(self):
        """Initialize all database managers."""
        self.medicine_db = MedicineDatabaseManager()
        self.interactions_db = DrugInteractionsManager()
        self.conditions_db = MedicalConditionsManager()
        self.dosage_db = DosageGuidelinesManager()
        self.side_effects_db = SideEffectsManager()
        self.effectiveness_db = DrugEffectivenessManager()
        self.patterns_db = PrescriptionPatternsManager()
        
        self._connected = False
    
    def connect_all(self) -> bool:
        """Connect to all databases."""
        try:
            connections = [
                self.medicine_db.connect(),
                self.interactions_db.connect(),
                self.conditions_db.connect(),
                self.dosage_db.connect(),
                self.side_effects_db.connect(),
                self.effectiveness_db.connect(),
                self.patterns_db.connect()
            ]
            
            self._connected = all(connections)
            if self._connected:
                print("✅ Connected to all medical databases")
            else:
                print("❌ Failed to connect to some databases")
            
            return self._connected
        except Exception as e:
            print(f"❌ Error connecting to databases: {e}")
            return False
    
    def close_all(self):
        """Close all database connections."""
        try:
            self.medicine_db.close()
            self.interactions_db.close()
            self.conditions_db.close()
            self.dosage_db.close()
            self.side_effects_db.close()
            self.effectiveness_db.close()
            self.patterns_db.close()
            self._connected = False
            print("✅ All database connections closed")
        except Exception as e:
            print(f"⚠️ Error closing databases: {e}")
    
    def get_comprehensive_medicine_info(self, medicine_name: str, 
                                      patient_age_months: Optional[int] = None,
                                      patient_weight_kg: Optional[float] = None,
                                      other_medicines: Optional[List[str]] = None,
                                      condition: Optional[str] = None) -> MedicalInsight:
        """Get comprehensive information about a medicine from all databases."""
        
        if not self._connected:
            if not self.connect_all():
                return MedicalInsight(medicine_name=medicine_name)
        
        insight = MedicalInsight(medicine_name=medicine_name, condition=condition)
        
        try:
            # 1. Basic medicine information
            insight.basic_info = self.medicine_db.get_medicine_info(medicine_name)
            
            # 2. Drug interactions
            if other_medicines:
                for other_med in other_medicines:
                    interaction = self.interactions_db.check_interactions(medicine_name, other_med)
                    if interaction:
                        insight.interactions.append(interaction)
            
            # Get all known interactions for this medicine
            all_interactions = self.interactions_db.get_drug_interactions(medicine_name)
            insight.interactions.extend(all_interactions)
            
            # 3. Side effects
            insight.side_effects = self.side_effects_db.get_side_effects_for_medicine(medicine_name)
            
            # 4. Dosage guidelines
            insight.dosage_guidelines = self.dosage_db.get_all_dosing_for_medicine(medicine_name)
            
            # Age-specific dosing if age provided
            if patient_age_months is not None:
                insight.age_appropriateness = self.dosage_db.check_age_appropriateness(
                    medicine_name, patient_age_months
                )
                
                if patient_weight_kg:
                    age_specific_dosing = self.dosage_db.get_dosage_for_age_weight(
                        medicine_name, patient_age_months, patient_weight_kg
                    )
                    if age_specific_dosing:
                        insight.dosage_guidelines = age_specific_dosing
            
            # 5. Effectiveness data
            insight.effectiveness_data = self.effectiveness_db.get_effectiveness_for_medicine(medicine_name)
            insight.conditions_treated = self.conditions_db.get_conditions_for_medicine(medicine_name)
            
            # 6. Prescription patterns
            insight.prescription_patterns = self.patterns_db.get_patterns_for_medicine(medicine_name)
            
            # Get combinations for specific condition if provided
            if condition:
                insight.common_combinations = self.patterns_db.get_common_combinations_for_condition(condition)
            
            # 7. Generate safety warnings
            insight.safety_warnings = self._generate_safety_warnings(insight)
            
            # 8. Generate clinical recommendations
            insight.clinical_recommendations = self._generate_clinical_recommendations(insight)
            
            # 9. Generate monitoring requirements
            insight.monitoring_requirements = self._generate_monitoring_requirements(insight)
            
        except Exception as e:
            print(f"⚠️ Error gathering comprehensive information: {e}")
        
        return insight
    
    def analyze_prescription_safety(self, medicines: List[str], 
                                  patient_age_months: Optional[int] = None) -> Dict:
        """Analyze safety of a complete prescription (multiple medicines)."""
        
        if not self._connected:
            if not self.connect_all():
                return {"error": "Database connection failed"}
        
        safety_analysis = {
            "medicines": medicines,
            "interactions_found": [],
            "age_inappropriate": [],
            "severe_side_effects": [],
            "monitoring_needed": [],
            "overall_safety_score": "unknown",
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Check all drug-drug interactions
            interactions = self.interactions_db.check_multiple_interactions(medicines)
            safety_analysis["interactions_found"] = interactions
            
            # Check age appropriateness if age provided
            if patient_age_months is not None:
                for medicine in medicines:
                    age_check = self.dosage_db.check_age_appropriateness(medicine, patient_age_months)
                    if not age_check.get("appropriate", True):
                        safety_analysis["age_inappropriate"].append({
                            "medicine": medicine,
                            "reason": age_check.get("reason", "Unknown reason")
                        })
            
            # Check for severe side effects
            for medicine in medicines:
                severe_effects = self.side_effects_db.get_severe_side_effects(medicine)
                if severe_effects:
                    safety_analysis["severe_side_effects"].extend([
                        {"medicine": medicine, "effect": effect} for effect in severe_effects
                    ])
            
            # Determine overall safety score
            safety_analysis["overall_safety_score"] = self._calculate_safety_score(
                len(interactions), len(safety_analysis["age_inappropriate"]), 
                len(safety_analysis["severe_side_effects"])
            )
            
            # Generate warnings and recommendations
            safety_analysis["warnings"] = self._generate_prescription_warnings(safety_analysis)
            safety_analysis["recommendations"] = self._generate_prescription_recommendations(safety_analysis)
            
        except Exception as e:
            safety_analysis["error"] = f"Analysis error: {e}"
        
        return safety_analysis
    
    def find_alternatives_for_condition(self, condition: str, 
                                      exclude_medicines: Optional[List[str]] = None,
                                      patient_age_months: Optional[int] = None) -> List[Dict]:
        """Find alternative medicines for a condition with comprehensive analysis."""
        
        if not self._connected:
            if not self.connect_all():
                return []
        
        alternatives = []
        exclude_medicines = exclude_medicines or []
        
        try:
            # Get all medicines for the condition
            condition_treatments = self.conditions_db.get_medicines_for_condition(condition)
            
            for treatment in condition_treatments:
                medicine_name = treatment['medicine_name']
                
                # Skip excluded medicines
                if medicine_name in exclude_medicines:
                    continue
                
                # Get comprehensive info for this alternative
                insight = self.get_comprehensive_medicine_info(
                    medicine_name, patient_age_months=patient_age_months, condition=condition
                )
                
                # Calculate suitability score
                suitability_score = self._calculate_suitability_score(insight, condition)
                
                alternative = {
                    "medicine_name": medicine_name,
                    "effectiveness_rating": treatment.get('effectiveness_rating', 0),
                    "treatment_line": treatment.get('treatment_line', 'unknown'),
                    "evidence_level": treatment.get('evidence_level', 'unknown'),
                    "suitability_score": suitability_score,
                    "safety_warnings": insight.safety_warnings[:3],  # Top 3 warnings
                    "common_side_effects": [
                        se for se in insight.side_effects 
                        if se.get('frequency_percentage', 0) >= 10
                    ][:3],  # Top 3 common side effects
                    "age_appropriate": True
                }
                
                # Check age appropriateness
                if patient_age_months and insight.age_appropriateness:
                    alternative["age_appropriate"] = insight.age_appropriateness.get("appropriate", True)
                    if not alternative["age_appropriate"]:
                        alternative["age_restriction_reason"] = insight.age_appropriateness.get("reason", "")
                
                alternatives.append(alternative)
            
            # Sort by suitability score
            alternatives.sort(key=lambda x: x['suitability_score'], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Error finding alternatives: {e}")
        
        return alternatives
    
    def get_condition_insights(self, condition: str) -> Dict:
        """Get comprehensive insights about treating a specific condition."""
        
        if not self._connected:
            if not self.connect_all():
                return {"error": "Database connection failed"}
        
        try:
            insights = {
                "condition": condition,
                "available_treatments": [],
                "first_line_treatments": [],
                "effectiveness_comparison": [],
                "prescription_patterns": {},
                "common_combinations": [],
                "treatment_guidelines": {}
            }
            
            # Get all treatments for the condition
            treatments = self.conditions_db.get_medicines_for_condition(condition)
            insights["available_treatments"] = treatments
            
            # Get first-line treatments
            first_line = self.conditions_db.get_first_line_treatments(condition)
            insights["first_line_treatments"] = first_line
            
            # Get effectiveness comparison
            effectiveness_comparison = self.effectiveness_db.compare_medicines_for_condition(condition)
            insights["effectiveness_comparison"] = effectiveness_comparison
            
            # Get prescription patterns
            patterns_summary = self.patterns_db.get_prescription_summary(condition)
            insights["prescription_patterns"] = patterns_summary
            
            # Get common combinations
            combinations = self.patterns_db.get_common_combinations_for_condition(condition)
            insights["common_combinations"] = combinations
            
            # Generate treatment guidelines summary
            insights["treatment_guidelines"] = self._generate_treatment_guidelines(condition, insights)
            
            return insights
            
        except Exception as e:
            return {"error": f"Error generating condition insights: {e}"}
    
    def _generate_safety_warnings(self, insight: MedicalInsight) -> List[str]:
        """Generate safety warnings based on comprehensive medicine data."""
        warnings = []
        
        # Severe interactions
        severe_interactions = [i for i in insight.interactions 
                             if i.get('interaction_severity') in ['severe', 'contraindicated']]
        for interaction in severe_interactions:
            warnings.append(f"⚠️ SEVERE INTERACTION with {interaction.get('drug2_name', 'unknown drug')}: {interaction.get('description', '')}")
        
        # Severe side effects
        severe_effects = [se for se in insight.side_effects 
                         if se.get('severity') in ['severe', 'life_threatening']]
        for effect in severe_effects:
            warnings.append(f"⚠️ SEVERE SIDE EFFECT: {effect.get('side_effect', '')} - {effect.get('description', '')}")
        
        # Age contraindications
        if insight.age_appropriateness and not insight.age_appropriateness.get("appropriate", True):
            warnings.append(f"⚠️ AGE RESTRICTION: {insight.age_appropriateness.get('reason', '')}")
        
        # Pediatric concerns
        pediatric_concerns = [dg for dg in insight.dosage_guidelines 
                            if 'CONTRAINDICATED' in dg.get('recommended_dose', '')]
        if pediatric_concerns:
            warnings.append("⚠️ CONTRAINDICATED in children - see dosage guidelines")
        
        return warnings[:5]  # Limit to top 5 warnings
    
    def _generate_clinical_recommendations(self, insight: MedicalInsight) -> List[str]:
        """Generate clinical recommendations based on comprehensive data."""
        recommendations = []
        
        # Dosage recommendations
        if insight.dosage_guidelines:
            best_dosing = insight.dosage_guidelines[0]
            recommendations.append(f"💊 Recommended dosing: {best_dosing.get('recommended_dose', '')}")
            
            if best_dosing.get('special_instructions'):
                recommendations.append(f"📋 Special instructions: {best_dosing.get('special_instructions', '')}")
        
        # Effectiveness insights
        if insight.effectiveness_data:
            best_indication = max(insight.effectiveness_data, 
                                key=lambda x: x.get('effectiveness_rating', 0))
            recommendations.append(f"✅ Most effective for: {best_indication.get('condition', '')} ({best_indication.get('effectiveness_rating', 0)}% effective)")
        
        # Common side effects to watch for
        common_effects = [se for se in insight.side_effects 
                         if se.get('frequency_percentage', 0) >= 10]
        if common_effects:
            top_effect = common_effects[0]
            recommendations.append(f"👁️ Monitor for: {top_effect.get('side_effect', '')} ({top_effect.get('frequency_percentage', 0)}% frequency)")
        
        # Prescription patterns insight
        if insight.prescription_patterns:
            pattern = insight.prescription_patterns[0]
            if pattern.get('secondary_medicine'):
                recommendations.append(f"🤝 Often combined with: {pattern.get('secondary_medicine', '')}")
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def _generate_monitoring_requirements(self, insight: MedicalInsight) -> List[str]:
        """Generate monitoring requirements based on medicine data."""
        monitoring = []
        
        # From dosage guidelines
        for guideline in insight.dosage_guidelines:
            if guideline.get('special_instructions'):
                monitoring.append(guideline.get('special_instructions', ''))
        
        # From prescription patterns
        for pattern in insight.prescription_patterns:
            if pattern.get('monitoring_requirements'):
                monitoring.append(pattern.get('monitoring_requirements', ''))
        
        # From side effects
        severe_effects = [se for se in insight.side_effects 
                         if se.get('severity') in ['severe', 'life_threatening']]
        for effect in severe_effects:
            if effect.get('when_to_seek_help'):
                monitoring.append(f"Seek help if: {effect.get('when_to_seek_help', '')}")
        
        # Remove duplicates and limit
        return list(set(monitoring))[:3]
    
    def _calculate_safety_score(self, interactions: int, age_issues: int, severe_effects: int) -> str:
        """Calculate overall safety score for a prescription."""
        total_concerns = interactions + age_issues + severe_effects
        
        if total_concerns == 0:
            return "LOW_RISK"
        elif total_concerns <= 2:
            return "MODERATE_RISK"
        else:
            return "HIGH_RISK"
    
    def _calculate_suitability_score(self, insight: MedicalInsight, condition: str) -> float:
        """Calculate suitability score for an alternative medicine."""
        score = 0.0
        
        # Effectiveness for the specific condition
        condition_effectiveness = [ed for ed in insight.effectiveness_data 
                                 if ed.get('condition', '').lower() == condition.lower()]
        if condition_effectiveness:
            score += condition_effectiveness[0].get('effectiveness_rating', 0) * 0.4
        
        # Safety score (inverse of severe side effects)
        severe_effects = len([se for se in insight.side_effects 
                            if se.get('severity') in ['severe', 'life_threatening']])
        safety_score = max(0, 100 - (severe_effects * 20))
        score += safety_score * 0.3
        
        # Evidence quality
        if insight.conditions_treated:
            evidence_bonus = {'high': 20, 'moderate': 10, 'low': 5, 'expert_opinion': 2}
            for treatment in insight.conditions_treated:
                if treatment.get('condition', '').lower() == condition.lower():
                    score += evidence_bonus.get(treatment.get('evidence_level', 'low'), 0) * 0.2
        
        # Age appropriateness
        if insight.age_appropriateness:
            if insight.age_appropriateness.get("appropriate", True):
                score += 10
            else:
                score -= 30  # Heavy penalty for age-inappropriate medicines
        
        return min(100.0, score)  # Cap at 100
    
    def _generate_prescription_warnings(self, safety_analysis: Dict) -> List[str]:
        """Generate warnings for prescription safety analysis."""
        warnings = []
        
        # Interaction warnings
        severe_interactions = [i for i in safety_analysis["interactions_found"] 
                             if i.get('interaction_severity') in ['severe', 'contraindicated']]
        if severe_interactions:
            warnings.append(f"🚨 {len(severe_interactions)} SEVERE drug interaction(s) detected")
        
        # Age warnings
        if safety_analysis["age_inappropriate"]:
            warnings.append(f"👶 {len(safety_analysis['age_inappropriate'])} medicine(s) inappropriate for patient age")
        
        # Side effect warnings
        if safety_analysis["severe_side_effects"]:
            warnings.append(f"⚠️ {len(safety_analysis['severe_side_effects'])} severe side effect risk(s)")
        
        return warnings
    
    def _generate_prescription_recommendations(self, safety_analysis: Dict) -> List[str]:
        """Generate recommendations for prescription safety analysis."""
        recommendations = []
        
        if safety_analysis["overall_safety_score"] == "HIGH_RISK":
            recommendations.append("🔴 HIGH RISK prescription - consider alternatives")
        elif safety_analysis["overall_safety_score"] == "MODERATE_RISK":
            recommendations.append("🟡 MODERATE RISK - enhanced monitoring recommended")
        else:
            recommendations.append("🟢 LOW RISK prescription")
        
        if safety_analysis["interactions_found"]:
            recommendations.append("Monitor closely for drug interaction symptoms")
        
        if safety_analysis["age_inappropriate"]:
            recommendations.append("Review age-appropriate alternatives")
        
        return recommendations
    
    def _generate_treatment_guidelines(self, condition: str, insights: Dict) -> Dict:
        """Generate treatment guidelines summary for a condition."""
        guidelines = {
            "first_line_count": len(insights["first_line_treatments"]),
            "total_options": len(insights["available_treatments"]),
            "evidence_quality": "unknown",
            "most_prescribed": "unknown",
            "success_rate": "unknown"
        }
        
        # Determine evidence quality
        high_evidence = len([t for t in insights["available_treatments"] 
                           if t.get('evidence_level') == 'high'])
        if high_evidence >= len(insights["available_treatments"]) * 0.7:
            guidelines["evidence_quality"] = "high"
        elif high_evidence >= len(insights["available_treatments"]) * 0.4:
            guidelines["evidence_quality"] = "moderate"
        else:
            guidelines["evidence_quality"] = "low"
        
        # Most prescribed medicine
        patterns = insights.get("prescription_patterns", {})
        if patterns.get("most_common_treatment"):
            guidelines["most_prescribed"] = patterns["most_common_treatment"]["primary"]
            guidelines["success_rate"] = f"{patterns['most_common_treatment']['success_rate']:.1f}%"
        
        return guidelines


def test_multi_database_manager():
    """Test the multi-database manager functionality."""
    print("🧪 Testing Multi-Database Manager...")
    
    manager = MultiDatabaseManager()
    
    if not manager.connect_all():
        print("❌ Failed to connect to databases")
        return False
    
    try:
        # Test 1: Comprehensive medicine info
        print("\n1️⃣ Testing comprehensive medicine analysis...")
        insight = manager.get_comprehensive_medicine_info(
            "Aspirin", 
            patient_age_months=300,  # 25 years old
            other_medicines=["Warfarin"]
        )
        print(f"   Medicine: {insight.medicine_name}")
        print(f"   Interactions found: {len(insight.interactions)}")
        print(f"   Side effects: {len(insight.side_effects)}")
        print(f"   Safety warnings: {len(insight.safety_warnings)}")
        print(f"   Clinical recommendations: {len(insight.clinical_recommendations)}")
        
        # Test 2: Prescription safety analysis
        print("\n2️⃣ Testing prescription safety analysis...")
        safety = manager.analyze_prescription_safety(
            ["Aspirin", "Warfarin"], 
            patient_age_months=300
        )
        print(f"   Overall safety: {safety['overall_safety_score']}")
        print(f"   Interactions: {len(safety['interactions_found'])}")
        print(f"   Warnings: {len(safety['warnings'])}")
        
        # Test 3: Finding alternatives
        print("\n3️⃣ Testing alternative medicine search...")
        alternatives = manager.find_alternatives_for_condition(
            "Hypertension", 
            exclude_medicines=["Atenolol"],
            patient_age_months=600  # 50 years old
        )
        print(f"   Alternatives found: {len(alternatives)}")
        if alternatives:
            best = alternatives[0]
            print(f"   Best alternative: {best['medicine_name']} (score: {best['suitability_score']:.1f})")
        
        # Test 4: Condition insights
        print("\n4️⃣ Testing condition insights...")
        insights = manager.get_condition_insights("Bacterial Pneumonia")
        print(f"   Available treatments: {len(insights.get('available_treatments', []))}")
        print(f"   First-line treatments: {len(insights.get('first_line_treatments', []))}")
        
        manager.close_all()
        print("\n✅ Multi-Database Manager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        manager.close_all()
        return False


if __name__ == "__main__":
    test_multi_database_manager() 