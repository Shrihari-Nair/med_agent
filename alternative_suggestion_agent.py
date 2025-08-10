#!/usr/bin/env python3
"""
Cost-Saving Alternative Suggestion Agent
Finds cost-effective alternatives for medicines using CrewAI and database lookup.
"""

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from medicine_database_manager import MedicineDatabaseManager
import json
import os
from typing import List, Dict, Any

class AlternativeSuggestionAgent:
    """AI agent for finding cost-effective medicine alternatives."""
    
    def __init__(self, api_key=None, db_path="medicines.db"):
        """
        Initialize the alternative suggestion agent.
        
        Args:
            api_key (str): Google Gemini API key (optional, can be set via env var)
            db_path (str): Path to the medicine database
        """
        # Set up Gemini LLM
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Initialize database manager
        self.db_manager = MedicineDatabaseManager(db_path)
        if not self.db_manager.connect():
            raise Exception("Failed to connect to medicine database")
        
        # Create the alternative suggestion agent
        self.agent = Agent(
            role="Cost-Saving Medicine Alternative Finder",
            goal="Find the most cost-effective alternative medicines in the same therapeutic class",
            backstory="""You are an expert pharmaceutical consultant specializing in finding 
            cost-effective medicine alternatives. You have extensive knowledge of medicine 
            classes, therapeutic equivalency, and cost optimization strategies. You always 
            prioritize patient safety while maximizing cost savings through generic alternatives 
            and therapeutic substitutions within the same medicine class.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def determine_medicine_generic(self, medicine_name: str) -> str:
        """
        Use AI to determine the generic name for a given medicine.
        
        Args:
            medicine_name (str): Name of the medicine
            
        Returns:
            str: Determined generic name
        """
        task = Task(
            description=f"""
            Determine the generic name for the following medicine.
            
            Medicine Name: {medicine_name}
            
            Instructions:
            1. Analyze the medicine name and determine its generic name
            2. Consider common brand names and their generic equivalents
            3. Return ONLY the generic name (e.g., "Acetaminophen" for "Tylenol")
            4. If the medicine name is already a generic, return it as is
            5. Use standard pharmaceutical naming conventions
            
            Examples:
            - "Tylenol" → "Acetaminophen"
            - "Advil" → "Ibuprofen"
            - "Zyrtec" → "Cetirizine"
            - "Prilosec" → "Omeprazole"
            - "Lipitor" → "Atorvastatin"
            - "Zoloft" → "Sertraline"
            
            Return the generic name only, nothing else.
            """,
            agent=self.agent,
            expected_output="Generic name of the medicine"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            # Clean up the result
            generic_name = str(result).strip().replace('"', '').replace("'", "")
            
            # Return the generic name as determined by AI
            return generic_name
            
        except Exception as e:
            print(f"Warning: Error determining generic for {medicine_name}: {e}")
            return medicine_name  # Default fallback - use medicine name as generic
    
    def process_medicine_alternatives(self, medicine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single medicine to find alternatives.
        
        Args:
            medicine_data (dict): Medicine data with name and quantity
            
        Returns:
            dict: Enhanced medicine data with alternatives
        """
        medicine_name = medicine_data["name"]
        quantity = medicine_data["quantity"]
        
        print(f"   🔍 Processing: {medicine_name}")
        
        # Get medicine info from database
        db_info = self.db_manager.get_medicine_info(medicine_name)
        
        if db_info:
            # Medicine found in database
            generic_name = db_info["generic_name"]
            original_price = db_info["price"]
            print(f"      📊 Found in DB: Generic={generic_name}, Price=${original_price}")
        else:
            # Medicine not in database, use AI to determine generic
            generic_name = self.determine_medicine_generic(medicine_name)
            original_price = self.db_manager.get_market_price_estimate(medicine_name, generic_name)
            print(f"      🤖 AI Classified: Generic={generic_name}, Est. Price=${original_price}")
        
        # Find alternatives
        alternatives = self.db_manager.find_cheapest_alternatives(
            medicine_name, generic_name, original_price, quantity, min_stock=10, limit=3
        )
        
        # Prepare result
        result = {
            "name": medicine_name,
            "quantity": quantity,
            "generic": generic_name,
            "original_price": original_price,
            "alternatives": alternatives
        }
        
        if alternatives:
            print(f"      ✅ Found {len(alternatives)} alternatives")
        else:
            print(f"      ⚠️  No alternatives found")
        
        return result
    
    def suggest_alternatives(self, medicines_json: str) -> str:
        """
        Main function to suggest alternatives for all medicines in the JSON.
        
        Args:
            medicines_json (str): JSON string from the text extraction agent
            
        Returns:
            str: Enhanced JSON with alternatives
        """
        try:
            # Parse input JSON
            data = json.loads(medicines_json)
            medicines = data.get("medicines", [])
            
            if not medicines:
                print("❌ No medicines found in input JSON")
                return json.dumps({"medicines": []})
            
            print(f"🔍 Processing {len(medicines)} medicines for alternatives...")
            
            # Process each medicine
            enhanced_medicines = []
            for medicine in medicines:
                enhanced_medicine = self.process_medicine_alternatives(medicine)
                enhanced_medicines.append(enhanced_medicine)
            
            # Create output JSON
            output_data = {
                "medicines": enhanced_medicines,
                "summary": {
                    "total_medicines": len(enhanced_medicines),
                    "medicines_with_alternatives": len([m for m in enhanced_medicines if m["alternatives"]]),
                    "total_alternatives_found": sum(len(m["alternatives"]) for m in enhanced_medicines)
                }
            }
            
            return json.dumps(output_data, indent=2)
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing input JSON: {e}")
            return json.dumps({"error": "Invalid JSON input"})
        except Exception as e:
            print(f"❌ Error processing alternatives: {e}")
            return json.dumps({"error": str(e)})
        finally:
            self.db_manager.close()
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close() 