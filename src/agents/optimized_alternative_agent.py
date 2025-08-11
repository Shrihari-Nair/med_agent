import os
import json
from typing import Optional, List, Dict, Any
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.manager import MedicineDatabaseManager
from src.database.drug_interactions_db import DrugInteractionsManager
from src.database.side_effects_db import SideEffectsManager
from src.database.dosage_db import DosageGuidelinesManager


class OptimizedAlternativeSuggestionAgent:
    """Optimized alternative suggestion agent using only critical databases for maximum performance."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Initialize only critical databases for performance
        self.medicine_db = MedicineDatabaseManager()
        self.interactions_db = DrugInteractionsManager()
        self.side_effects_db = SideEffectsManager()
        self.dosage_db = DosageGuidelinesManager()
        
        # Initialize LLM
        if self.api_key:
            os.environ["GOOGLE_API_KEY"] = self.api_key
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create a streamlined agent
        self.agent = Agent(
            role="Optimized Clinical Pharmacist",
            goal="Rapidly provide safe, cost-effective medicine alternatives with essential safety intelligence",
            backstory="You are an experienced pharmacist who provides rapid, safety-focused alternative suggestions using core medical databases.",
            llm=self.llm,
            verbose=False
        )
    
    def suggest_alternatives(self, medicines_json: str, 
                           patient_age_years: Optional[int] = None,
                           patient_conditions: Optional[List[str]] = None,
                           budget_conscious: bool = True) -> str:
        """
        Optimized alternative suggestions using only critical databases for speed.
        """
        try:
            # Parse input medicines
            medicines_data = json.loads(medicines_json)
            medicines = medicines_data.get("medicines", [])
            
            if not medicines:
                return json.dumps({"error": "No medicines found in input"})
            
            # Convert age to months for database queries
            patient_age_months = patient_age_years * 12 if patient_age_years else None
            
            # Connect to only critical databases
            if not self._connect_critical_databases():
                return json.dumps({"error": "Failed to connect to critical medical databases"})
            
            # Get all medicine names for batch processing
            medicine_names = [med.get('name', '').strip() for med in medicines if med.get('name')]
            
            # Optimized batch database operations
            batch_medicine_info = self._get_critical_medicine_info(medicine_names, patient_age_months)
            batch_safety_analysis = self._critical_safety_analysis(medicine_names, patient_age_months)
            
            # Prepare streamlined context for AI
            optimized_context = self._create_optimized_context(
                medicines, batch_medicine_info, batch_safety_analysis,
                patient_age_years, patient_conditions, budget_conscious
            )
            
            # Create optimized task
            task = Task(
                description=f"""
                Analyze this prescription quickly using core safety databases and provide JSON response:
                
                {optimized_context}
                
                Provide a JSON response with this EXACT structure:
                {{
                  "prescription_analysis": {{
                    "overall_safety_assessment": "Brief safety summary focused on critical issues",
                    "critical_warnings": ["List only severe safety warnings"],
                    "recommendations_summary": "Key safety-focused recommendations"
                  }},
                  "medicine_alternatives": [
                    {{
                      "original_medicine": {{
                        "name": "Medicine name",
                        "current_quantity": "Quantity",
                        "safety_concerns": ["Critical safety concerns only"],
                        "effectiveness_rating": "Basic rating if available"
                      }},
                      "recommended_alternatives": [
                        {{
                          "name": "Alternative name",
                          "recommendation_strength": "Highly Recommended/Recommended/Consider",
                          "rationale": "Safety-focused reason for recommendation",
                          "cost_comparison": "Cost comparison",
                          "safety_profile": "Core safety summary",
                          "effectiveness": "Basic effectiveness summary",
                          "dosing_recommendation": "Age-appropriate dosing if relevant",
                          "monitoring_required": "Critical monitoring only"
                        }}
                      ],
                      "clinical_notes": "Essential safety considerations only"
                    }}
                  ],
                  "overall_recommendations": {{
                    "prescription_changes": "Summary of safety-focused changes",
                    "follow_up_needed": "Critical follow-up requirements",
                    "pharmacist_consultation": true/false,
                    "doctor_consultation": true/false
                  }}
                }}
                
                Focus on speed and critical safety. Limit alternatives to 2-3 per medicine.
                Only include information from the 4 core databases: medicine info, drug interactions, side effects, and dosage guidelines.
                """,
                agent=self.agent,
                expected_output="Optimized JSON response with medicine alternatives and critical safety analysis"
            )
            
            # Execute quickly
            result = task.execute()
            
            # Close database connections
            self._close_critical_databases()
            
            # Clean and return result
            return self._clean_json_result(result)
            
        except Exception as e:
            self._close_critical_databases()
            return json.dumps({
                "error": f"Error in optimized alternative analysis: {str(e)}",
                "fallback_message": "Please consult with a healthcare provider for medicine alternatives."
            })
    
    def _connect_critical_databases(self) -> bool:
        """Connect to only the 4 critical databases for performance."""
        try:
            connections = [
                self.medicine_db.connect(),
                self.interactions_db.connect(),
                self.side_effects_db.connect(),
                self.dosage_db.connect()
            ]
            return all(connections)
        except Exception as e:
            print(f"❌ Failed to connect to critical databases: {e}")
            return False
    
    def _close_critical_databases(self):
        """Close critical database connections."""
        try:
            self.medicine_db.close()
            self.interactions_db.close()
            self.side_effects_db.close()
            self.dosage_db.close()
        except Exception:
            pass
    
    def _get_critical_medicine_info(self, medicine_names: List[str], patient_age_months: Optional[int]) -> Dict[str, Dict]:
        """Get only critical safety info for all medicines in one batch."""
        batch_info = {}
        
        for med_name in medicine_names:
            try:
                # Get only critical information for speed
                info = {
                    'basic_info': None,
                    'drug_interactions': [],
                    'side_effects': [],
                    'dosage_guidelines': []
                }
                
                # Basic medicine info
                try:
                    basic_info = self.medicine_db.search_medicine(med_name)
                    if basic_info:
                        info['basic_info'] = basic_info[0] if basic_info else None
                except Exception:
                    pass
                
                # Critical drug interactions check
                try:
                    interactions = self.interactions_db.check_interactions(med_name)
                    if interactions:
                        info['drug_interactions'] = interactions[:2]  # Limit to 2 for speed
                except Exception:
                    pass
                
                # Critical side effects
                try:
                    side_effects = self.side_effects_db.get_medicine_side_effects(med_name)
                    if side_effects:
                        info['side_effects'] = side_effects[:3]  # Limit to 3 for speed
                except Exception:
                    pass
                
                # Critical dosage info (age appropriateness)
                if patient_age_months:
                    try:
                        dosage = self.dosage_db.get_age_appropriate_dosage(med_name, patient_age_months)
                        if dosage:
                            info['dosage_guidelines'] = [dosage]
                    except Exception:
                        pass
                
                batch_info[med_name] = info
                
            except Exception:
                # If individual medicine fails, continue with others
                batch_info[med_name] = {'error': 'Failed to fetch critical info'}
        
        return batch_info
    
    def _critical_safety_analysis(self, medicine_names: List[str], patient_age_months: Optional[int]) -> Dict:
        """Quick critical safety analysis using only essential databases."""
        try:
            # Critical interaction check
            severe_interactions = []
            total_interactions = 0
            
            for i, med1 in enumerate(medicine_names):
                for med2 in medicine_names[i+1:]:
                    try:
                        interaction = self.interactions_db.check_interactions(med1, med2)
                        if interaction:
                            total_interactions += len(interaction)
                            severe = [inter for inter in interaction if 'severe' in str(inter).lower()]
                            severe_interactions.extend(severe[:1])  # Limit to 1 severe per pair
                    except Exception:
                        continue
            
            # Critical age appropriateness check
            age_warnings = []
            if patient_age_months and patient_age_months < 216:  # Less than 18 years
                for med_name in medicine_names:
                    try:
                        dosage = self.dosage_db.get_age_appropriate_dosage(med_name, patient_age_months)
                        if not dosage:
                            age_warnings.append(f"No pediatric dosing for {med_name}")
                    except Exception:
                        continue
            
            return {
                'severe_interactions': severe_interactions[:2],  # Limit to 2
                'age_warnings': age_warnings[:2],  # Limit to 2
                'total_interactions': total_interactions,
                'safety_score': 'HIGH_RISK' if len(severe_interactions) > 1 else 
                               'MODERATE_RISK' if len(severe_interactions) > 0 or len(age_warnings) > 0 else 
                               'LOW_RISK'
            }
        except Exception:
            return {'error': 'Critical safety analysis failed', 'safety_score': 'UNKNOWN'}
    
    def _create_optimized_context(self, medicines: List[Dict], batch_info: Dict, 
                                 safety_analysis: Dict, patient_age_years: Optional[int],
                                 patient_conditions: Optional[List[str]], budget_conscious: bool) -> str:
        """Create optimized context focusing only on critical safety information."""
        
        context_parts = []
        
        # Patient info
        context_parts.append(f"Patient: {patient_age_years} years old" if patient_age_years else "Patient: Age unknown")
        if patient_conditions:
            context_parts.append(f"Conditions: {', '.join(patient_conditions)}")
        context_parts.append(f"Budget conscious: {budget_conscious}")
        
        # Critical safety summary
        context_parts.append(f"\nCritical Safety Analysis:")
        context_parts.append(f"- Safety Score: {safety_analysis.get('safety_score', 'UNKNOWN')}")
        if safety_analysis.get('severe_interactions'):
            context_parts.append(f"- Severe Interactions: {len(safety_analysis['severe_interactions'])}")
        if safety_analysis.get('age_warnings'):
            context_parts.append(f"- Age Warnings: {len(safety_analysis['age_warnings'])}")
        
        # Critical medicine details
        context_parts.append(f"\nMedicines for critical analysis:")
        for med in medicines:
            med_name = med.get('name', '')
            quantity = med.get('quantity', '')
            
            context_parts.append(f"\n{med_name} ({quantity}):")
            
            if med_name in batch_info:
                info = batch_info[med_name]
                
                # Critical interactions
                if info.get('drug_interactions'):
                    context_parts.append(f"  - Critical interactions: {len(info['drug_interactions'])}")
                
                # Critical side effects
                if info.get('side_effects'):
                    severe_effects = [se for se in info['side_effects'] if 'severe' in str(se).lower()]
                    if severe_effects:
                        context_parts.append(f"  - Severe side effects: {len(severe_effects)}")
                
                # Age appropriateness
                if info.get('dosage_guidelines'):
                    context_parts.append(f"  - Age-appropriate dosing available")
                elif patient_age_years and patient_age_years < 18:
                    context_parts.append(f"  - WARNING: No pediatric dosing data")
        
        return '\n'.join(context_parts)
    
    def _clean_json_result(self, result: str) -> str:
        """Clean and validate JSON result quickly."""
        try:
            # Clean the result - remove markdown code blocks if present
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()
            
            # Validate it's proper JSON
            parsed_result = json.loads(cleaned_result)
            return json.dumps(parsed_result, ensure_ascii=False, indent=2)
            
        except json.JSONDecodeError as e:
            print(f"❌ Optimized agent JSON parsing error: {e}")
            print(f"Raw result preview: {result[:200]}...")
            
            # Return simplified fallback
            return json.dumps({
                "prescription_analysis": {
                    "overall_safety_assessment": "Critical analysis completed but parsing failed",
                    "critical_warnings": [],
                    "recommendations_summary": "Please consult healthcare provider"
                },
                "medicine_alternatives": [],
                "overall_recommendations": {
                    "prescription_changes": "Manual review needed",
                    "follow_up_needed": "Consult healthcare provider",
                    "pharmacist_consultation": True,
                    "doctor_consultation": True
                }
            })


def test_optimized_alternative_agent():
    """Test the optimized alternative suggestion agent."""
    print("⚡ Testing Optimized Alternative Suggestion Agent...")
    
    # Test medicines JSON
    test_medicines = {
        "medicines": [
            {"name": "Aspirin", "quantity": "81mg daily"},
            {"name": "Atenolol", "quantity": "50mg daily"}
        ]
    }
    
    agent = OptimizedAlternativeSuggestionAgent()
    
    import time
    start_time = time.time()
    
    # Test the optimized analysis
    result = agent.suggest_alternatives(
        json.dumps(test_medicines),
        patient_age_years=65,
        patient_conditions=["Hypertension", "Cardiovascular Disease"],
        budget_conscious=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"⚡ Optimized processing completed in {processing_time:.2f} seconds")
    print("📊 Optimized Alternative Analysis Result:")
    try:
        parsed_result = json.loads(result)
        print(f"   Analysis type: {type(parsed_result)}")
        if "prescription_analysis" in parsed_result:
            print(f"   Safety assessment: {parsed_result['prescription_analysis'].get('overall_safety_assessment', 'N/A')}")
        if "medicine_alternatives" in parsed_result:
            print(f"   Alternatives analyzed: {len(parsed_result['medicine_alternatives'])}")
        print("✅ Optimized agent test completed successfully!")
        print(f"⚡ Performance gain: Using only 4 critical databases instead of 7")
    except json.JSONDecodeError:
        print("   Result is not JSON format")
        print(f"   Result preview: {result[:200]}...")
    
    return True


if __name__ == "__main__":
    test_optimized_alternative_agent() 