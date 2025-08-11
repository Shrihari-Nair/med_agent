"""
Enhanced Alternative Suggestion Agent
AI agent with multi-database intelligence for finding cost-effective medicine alternatives.
"""

import os
import json
from typing import Optional, List, Dict, Any
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.multi_db_manager import MultiDatabaseManager


class FastEnhancedAlternativeSuggestionAgent:
    """Fast version of enhanced alternative suggestion agent with optimized database access."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.multi_db = MultiDatabaseManager()
        
        # Initialize LLM
        if self.api_key:
            os.environ["GOOGLE_API_KEY"] = self.api_key
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create a simplified agent
        self.agent = Agent(
            role="Fast Clinical Pharmacist",
            goal="Quickly provide safe, cost-effective medicine alternatives with database insights",
            backstory="You are an experienced pharmacist who provides rapid, evidence-based alternative suggestions using medical databases.",
            llm=self.llm,
            verbose=False  # Reduce output for speed
        )
    
    def suggest_alternatives(self, medicines_json: str, 
                           patient_age_years: Optional[int] = None,
                           patient_conditions: Optional[List[str]] = None,
                           budget_conscious: bool = True) -> str:
        """
        Fast alternative suggestions using optimized database access.
        """
        try:
            # Parse input medicines
            medicines_data = json.loads(medicines_json)
            medicines = medicines_data.get("medicines", [])
            
            if not medicines:
                return json.dumps({"error": "No medicines found in input"})
            
            # Convert age to months for database queries
            patient_age_months = patient_age_years * 12 if patient_age_years else None
            
            # Connect to databases once
            if not self.multi_db.connect_all():
                return json.dumps({"error": "Failed to connect to medical databases"})
            
            # Get all medicine names for batch processing
            medicine_names = [med.get('name', '').strip() for med in medicines if med.get('name')]
            
            # Batch database operations for speed
            batch_medicine_info = self._get_batch_medicine_info(medicine_names, patient_age_months)
            batch_safety_analysis = self._quick_safety_analysis(medicine_names, patient_age_months)
            
            # Prepare simplified context for AI
            simplified_context = self._create_simplified_context(
                medicines, batch_medicine_info, batch_safety_analysis,
                patient_age_years, patient_conditions, budget_conscious
            )
            
            # Create optimized task
            task = Task(
                description=f"""
                Analyze this prescription quickly and provide JSON response:
                
                {simplified_context}
                
                Provide a JSON response with this EXACT structure:
                {{
                  "prescription_analysis": {{
                    "overall_safety_assessment": "Brief safety summary",
                    "critical_warnings": ["List critical warnings"],
                    "recommendations_summary": "Key recommendations"
                  }},
                  "medicine_alternatives": [
                    {{
                      "original_medicine": {{
                        "name": "Medicine name",
                        "current_quantity": "Quantity",
                        "safety_concerns": ["List safety concerns"],
                        "effectiveness_rating": "Rating if available"
                      }},
                      "recommended_alternatives": [
                        {{
                          "name": "Alternative name",
                          "recommendation_strength": "Highly Recommended/Recommended/Consider",
                          "rationale": "Brief reason for recommendation",
                          "cost_comparison": "Cost comparison",
                          "safety_profile": "Safety summary",
                          "effectiveness": "Effectiveness summary",
                          "dosing_recommendation": "Dosing if relevant",
                          "monitoring_required": "Monitoring if needed"
                        }}
                      ],
                      "clinical_notes": "Important clinical considerations"
                    }}
                  ],
                  "overall_recommendations": {{
                    "prescription_changes": "Summary of changes",
                    "follow_up_needed": "Follow-up requirements",
                    "pharmacist_consultation": true/false,
                    "doctor_consultation": true/false
                  }}
                }}
                
                Focus on speed and safety. Limit alternatives to 2-3 per medicine.
                """,
                agent=self.agent,
                expected_output="Fast JSON response with medicine alternatives and safety analysis"
            )
            
            # Execute quickly
            result = task.execute()
            
            # Close database connections
            self.multi_db.close_all()
            
            # Clean and return result
            return self._clean_json_result(result)
            
        except Exception as e:
            self.multi_db.close_all()
            return json.dumps({
                "error": f"Error in fast alternative analysis: {str(e)}",
                "fallback_message": "Please consult with a healthcare provider for medicine alternatives."
            })
    
    def _get_batch_medicine_info(self, medicine_names: List[str], patient_age_months: Optional[int]) -> Dict[str, Dict]:
        """Get essential info for all medicines in one batch to improve speed."""
        batch_info = {}
        
        for med_name in medicine_names:
            try:
                # Get only essential information quickly
                info = {
                    'drug_interactions': [],
                    'side_effects': [],
                    'dosage_guidelines': [],
                    'effectiveness_data': [],
                    'conditions_treated': []
                }
                
                # Quick drug interactions check
                interactions = self.multi_db.drug_interactions_manager.check_interactions(med_name)
                if interactions:
                    info['drug_interactions'] = interactions[:3]  # Limit to 3 for speed
                
                # Quick side effects
                side_effects = self.multi_db.side_effects_manager.get_medicine_side_effects(med_name)
                if side_effects:
                    info['side_effects'] = side_effects[:4]  # Limit to 4 for speed
                
                # Quick dosage info
                if patient_age_months:
                    dosage = self.multi_db.dosage_manager.get_age_appropriate_dosage(med_name, patient_age_months)
                    if dosage:
                        info['dosage_guidelines'] = [dosage]
                
                # Quick effectiveness
                effectiveness = self.multi_db.effectiveness_manager.get_medicine_effectiveness(med_name)
                if effectiveness:
                    info['effectiveness_data'] = effectiveness[:2]  # Limit to 2 for speed
                
                batch_info[med_name] = info
                
            except Exception:
                # If individual medicine fails, continue with others
                batch_info[med_name] = {'error': 'Failed to fetch info'}
        
        return batch_info
    
    def _quick_safety_analysis(self, medicine_names: List[str], patient_age_months: Optional[int]) -> Dict:
        """Quick safety analysis without deep database queries."""
        try:
            # Quick check for severe interactions
            severe_interactions = []
            for i, med1 in enumerate(medicine_names):
                for med2 in medicine_names[i+1:]:
                    interaction = self.multi_db.drug_interactions_manager.check_interactions(med1, med2)
                    if interaction and any('severe' in str(inter).lower() for inter in interaction):
                        severe_interactions.extend(interaction[:1])  # Limit to 1 per pair
            
            # Quick age appropriateness check
            age_warnings = []
            if patient_age_months and patient_age_months < 216:  # Less than 18 years
                for med_name in medicine_names:
                    dosage = self.multi_db.dosage_manager.get_age_appropriate_dosage(med_name, patient_age_months)
                    if not dosage:
                        age_warnings.append(f"No pediatric dosing for {med_name}")
            
            return {
                'severe_interactions': severe_interactions[:3],  # Limit to 3
                'age_warnings': age_warnings[:3],  # Limit to 3
                'total_interactions': len(severe_interactions),
                'safety_score': 'HIGH_RISK' if len(severe_interactions) > 2 else 
                               'MODERATE_RISK' if len(severe_interactions) > 0 or len(age_warnings) > 0 else 
                               'LOW_RISK'
            }
        except Exception:
            return {'error': 'Safety analysis failed', 'safety_score': 'UNKNOWN'}
    
    def _create_simplified_context(self, medicines: List[Dict], batch_info: Dict, 
                                 safety_analysis: Dict, patient_age_years: Optional[int],
                                 patient_conditions: Optional[List[str]], budget_conscious: bool) -> str:
        """Create simplified context for faster AI processing."""
        
        context_parts = []
        
        # Patient info
        context_parts.append(f"Patient: {patient_age_years} years old" if patient_age_years else "Patient: Age unknown")
        if patient_conditions:
            context_parts.append(f"Conditions: {', '.join(patient_conditions)}")
        context_parts.append(f"Budget conscious: {budget_conscious}")
        
        # Safety summary
        context_parts.append(f"\nSafety Analysis:")
        context_parts.append(f"- Safety Score: {safety_analysis.get('safety_score', 'UNKNOWN')}")
        if safety_analysis.get('severe_interactions'):
            context_parts.append(f"- Severe Interactions: {len(safety_analysis['severe_interactions'])}")
        if safety_analysis.get('age_warnings'):
            context_parts.append(f"- Age Warnings: {len(safety_analysis['age_warnings'])}")
        
        # Medicine details (simplified)
        context_parts.append(f"\nMedicines to analyze:")
        for med in medicines:
            med_name = med.get('name', '')
            quantity = med.get('quantity', '')
            
            context_parts.append(f"\n{med_name} ({quantity}):")
            
            if med_name in batch_info:
                info = batch_info[med_name]
                
                # Key interactions
                if info.get('drug_interactions'):
                    context_parts.append(f"  - Interactions: {len(info['drug_interactions'])}")
                
                # Key side effects
                if info.get('side_effects'):
                    context_parts.append(f"  - Side effects: {len(info['side_effects'])}")
                
                # Effectiveness
                if info.get('effectiveness_data'):
                    context_parts.append(f"  - Effectiveness data available")
        
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
            print(f"❌ Fast agent JSON parsing error: {e}")
            print(f"Raw result preview: {result[:200]}...")
            
            # Return simplified fallback
            return json.dumps({
                "prescription_analysis": {
                    "overall_safety_assessment": "Analysis completed but parsing failed",
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


# Keep the original class for compatibility but use fast version by default
class EnhancedAlternativeSuggestionAgent(FastEnhancedAlternativeSuggestionAgent):
    """Alias for the fast version - maintains compatibility."""
    pass


def test_fast_enhanced_alternative_agent():
    """Test the fast enhanced alternative suggestion agent."""
    print("🚀 Testing Fast Enhanced Alternative Suggestion Agent...")
    
    # Test medicines JSON
    test_medicines = {
        "medicines": [
            {"name": "Aspirin", "quantity": "81mg daily"},
            {"name": "Atenolol", "quantity": "50mg daily"}
        ]
    }
    
    agent = FastEnhancedAlternativeSuggestionAgent()
    
    import time
    start_time = time.time()
    
    # Test the fast enhanced analysis
    result = agent.suggest_alternatives(
        json.dumps(test_medicines),
        patient_age_years=65,
        patient_conditions=["Hypertension", "Cardiovascular Disease"],
        budget_conscious=True
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"⚡ Processing completed in {processing_time:.2f} seconds")
    print("📊 Fast Enhanced Alternative Analysis Result:")
    try:
        parsed_result = json.loads(result)
        print(f"   Analysis type: {type(parsed_result)}")
        if "prescription_analysis" in parsed_result:
            print(f"   Safety assessment: {parsed_result['prescription_analysis'].get('overall_safety_assessment', 'N/A')}")
        if "medicine_alternatives" in parsed_result:
            print(f"   Alternatives analyzed: {len(parsed_result['medicine_alternatives'])}")
        print("✅ Fast enhanced agent test completed successfully!")
    except json.JSONDecodeError:
        print("   Result is not JSON format")
        print(f"   Result preview: {result[:200]}...")
    
    return True


if __name__ == "__main__":
    test_fast_enhanced_alternative_agent() 