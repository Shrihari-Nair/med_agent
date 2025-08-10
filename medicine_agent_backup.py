from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import os

class MedicineExtractionAgent:
    """AI agent for extracting medicine names and quantities from text."""
    
    def __init__(self, api_key=None):
        """
        Initialize the medicine extraction agent.
        
        Args:
            api_key (str): Google Gemini API key (optional, can be set via env var)
        """
        # Set up Gemini LLM
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create the medicine extraction agent
        self.agent = Agent(
            role="Medicine Data Extractor",
            goal="Extract medicine names and quantities from medical documents accurately",
            backstory="""You are an expert medical data analyst specialized in extracting 
            medicine information from various document formats. You have extensive experience 
            in pharmaceutical terminology and can identify medicine names and quantities 
            even when they appear in different formats or abbreviations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def extract_medicines(self, text_content):
        """
        Extract medicine names and quantities from text content.
        
        Args:
            text_content (str): Text content extracted from PDF
            
        Returns:
            list: List of dictionaries containing medicine name and quantity
        """
        # Create the extraction task
        task = Task(
            description=f"""
            Analyze the following text content and extract ONLY medicine names and their quantities.
            
            Text Content:
            {text_content}
            
            Instructions:
            1. Identify all medicine names in the text
            2. Extract the corresponding quantities for each medicine
            3. Return ONLY the medicine name and quantity, nothing else
            4. If a medicine appears multiple times, combine quantities if possible
            5. Handle various quantity formats (tablets, capsules, mg, ml, etc.)
            6. Return the result as a JSON array with 'name' and 'quantity' fields
            
            Expected Output Format:
            [
                {{"name": "Medicine Name", "quantity": "10 tablets"}},
                {{"name": "Another Medicine", "quantity": "500mg"}}
            ]
            
            Be precise and only include medicines that are clearly mentioned with quantities.
            """,
            agent=self.agent,
            expected_output="JSON array of medicines with names and quantities"
        )
        
        # Create crew and execute task
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            
            # Try to parse the result as JSON
            try:
                # Extract JSON from the result if it's wrapped in text
                if isinstance(result, str):
                    # Look for JSON array in the result
                    start_idx = result.find('[')
                    end_idx = result.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = result[start_idx:end_idx]
                        medicines = json.loads(json_str)
                    else:
                        # If no JSON found, return empty list
                        medicines = []
                elif isinstance(result, list):
                    # If result is already a list, use it directly
                    medicines = result
                else:
                    medicines = []
                
                # Validate the structure
                if isinstance(medicines, list):
                    validated_medicines = []
                    for medicine in medicines:
                        if isinstance(medicine, dict) and 'name' in medicine and 'quantity' in medicine:
                            validated_medicines.append({
                                'name': str(medicine['name']).strip(),
                                'quantity': str(medicine['quantity']).strip()
                            })
                    return json.dumps({"medicines": validated_medicines})
                else:
                    return json.dumps({"medicines": []})
                    
            except json.JSONDecodeError:
                print("Warning: Could not parse agent output as JSON. Returning empty result.")
                return json.dumps({"medicines": []})
                
        except Exception as e:
            print(f"Error during extraction: {str(e)}")
            return json.dumps({"medicines": []}) 