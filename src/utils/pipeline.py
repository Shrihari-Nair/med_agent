#!/usr/bin/env python3
"""
Medicine Extraction and Alternative Suggestion Pipeline
Combines text extraction agent with cost-saving alternative suggestion agent.
"""

import sys
import json
import os
from src.utils.pdf_reader import PDFReader
from src.agents.medicine_agent import MedicineExtractionAgent
from src.agents.optimized_alternative_agent import OptimizedAlternativeSuggestionAgent

def main():
    """Main function to run the complete medicine extraction and alternative suggestion pipeline."""
    
    # Check if PDF file path is provided
    if len(sys.argv) != 2:
        print("Usage: python main_pipeline.py <path_to_pdf>")
        print("Example: python main_pipeline.py medicine_list.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        print("🏥 MEDICINE EXTRACTION & ALTERNATIVE SUGGESTION PIPELINE")
        print("=" * 70)
        print(f"📄 Processing PDF: {pdf_path}")
        
        # Step 1: Extract text from PDF
        print("\n📖 STEP 1: Extracting text from PDF...")
        pdf_reader = PDFReader()
        
        # Get PDF info
        pdf_info = pdf_reader.get_pdf_info(pdf_path)
        print(f"   📊 PDF Info: {pdf_info['pages']} pages, {pdf_info['file_size']} bytes")
        
        # Extract text
        text_content = pdf_reader.extract_text(pdf_path)
        print(f"   ✅ Text extracted successfully ({len(text_content)} characters)")
        
        if not text_content.strip():
            print("❌ No text content found in PDF. Please check if the PDF contains readable text.")
            sys.exit(1)
        
        # Step 2: Extract medicines using first agent
        print("\n🧬 STEP 2: Extracting medicines from text...")
        
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️  Warning: GOOGLE_API_KEY environment variable not set.")
            print("   Please set your Gemini API key: export GOOGLE_API_KEY='your_api_key'")
            print("   Or provide it as a parameter in the code.")
        
        extraction_agent = MedicineExtractionAgent()
        print("   ✅ Medicine extraction agent initialized")
        
        # Extract medicines
        medicines_json = extraction_agent.extract_medicines(text_content)
        
        # Parse and display results
        try:
            medicines_data = json.loads(medicines_json)
            medicines = medicines_data.get("medicines", [])
            
            if medicines:
                print(f"   ✅ Found {len(medicines)} medicines:")
                for i, medicine in enumerate(medicines, 1):
                    print(f"      {i}. {medicine['name']} - {medicine['quantity']}")
            else:
                print("   ⚠️  No medicines found in the document.")
                print("   Proceeding with empty medicine list...")
                
        except json.JSONDecodeError:
            print("   ⚠️  Could not parse medicine extraction results.")
            print("   Proceeding with empty medicine list...")
            medicines = []
        
        # Step 3: Find cost-effective alternatives
        print("\n💰 STEP 3: Finding cost-effective alternatives...")
        
        # Check if database exists
        if not os.path.exists("data/medicines.db"):
            print("❌ Medicine database not found!")
            print("   Please create the database first: python src/database/create_db.py")
            sys.exit(1)
        
        alternative_agent = OptimizedAlternativeSuggestionAgent()
        print("   ✅ Alternative suggestion agent initialized")
        
        # Create input JSON for alternative agent
        input_json = json.dumps({"medicines": medicines})
        
        # Find alternatives
        alternatives_result = alternative_agent.suggest_alternatives(input_json)
        
        # Parse and display results
        try:
            alternatives_data = json.loads(alternatives_result)
            
            if "error" in alternatives_data:
                print(f"   ❌ Error in alternative suggestion: {alternatives_data['error']}")
                sys.exit(1)
            
            enhanced_medicines = alternatives_data.get("medicines", [])
            summary = alternatives_data.get("summary", {})
            
            print(f"\n📋 FINAL RESULTS:")
            print("=" * 70)
            print(f"   Total medicines processed: {summary.get('total_medicines', 0)}")
            print(f"   Medicines with alternatives: {summary.get('medicines_with_alternatives', 0)}")
            print(f"   Total alternatives found: {summary.get('total_alternatives_found', 0)}")
            
            # Display detailed results
            for i, medicine in enumerate(enhanced_medicines, 1):
                print(f"\n   💊 {i}. {medicine['name']} - {medicine['quantity']}")
                print(f"      Generic: {medicine['generic']}")
                print(f"      Original Price: ${medicine['original_price']}")
                
                alternatives = medicine.get('alternatives', [])
                if alternatives:
                    print(f"      💰 Cost-effective alternatives:")
                    for j, alt in enumerate(alternatives, 1):
                        print(f"         {j}. {alt['name']} - ${alt['price']}")
                        print(f"            Manufacturer: {alt['manufacturer']}")
                        print(f"            Stock Available: {alt['stock_quantity']} units")
                        print(f"            Generic Name: {alt['generic_name']}")
                        print(f"            Therapeutic Class: {alt['class']}")
                        print(f"            Per unit savings: ${alt['savings_amount']} ({alt['savings_percent']}%)")
                        print(f"            Total savings for {alt['quantity_needed']}: ${alt['total_savings']}")
                        print("")
                else:
                    print(f"      ⚠️  No cost-effective alternatives found")
            
            # Save results to JSON file
            output_file = "medicine_alternatives.json"
            with open(output_file, 'w') as f:
                json.dump(alternatives_data, f, indent=2)
            print(f"\n💾 Complete results saved to: {output_file}")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Error parsing alternative results: {e}")
            print(f"   Raw result: {alternatives_result}")
        
        print("\n✅ Pipeline completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 