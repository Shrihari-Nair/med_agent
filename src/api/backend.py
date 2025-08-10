#!/usr/bin/env python3
"""
FastAPI Backend for Medicine Alternative Suggestion System
Serves the frontend and processes prescription files.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import tempfile
import os
import json
from pathlib import Path

# Import our existing pipeline components
from src.utils.pdf_reader import PDFReader
from src.agents.medicine_agent import MedicineExtractionAgent
from src.agents.alternative_suggestion_agent import AlternativeSuggestionAgent

# Import the new fuzzy search module (safe addition)
from src.utils.fuzzy_search import FuzzyMedicineSearch, search_medicine_fuzzy

app = FastAPI(title="Medicine Alternative API", version="1.0.0")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend dist folder when built)
frontend_dist = Path("generic-saver-bot/dist")
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")

def process_prescription_file(file_path: str) -> dict:
    """
    Process prescription file and return alternatives.
    Converts main_pipeline.py logic to function-based approach.
    """
    try:
        print(f"🔍 Processing file: {file_path}")
        
        # Step 1: Extract text from PDF
        pdf_reader = PDFReader()
        text_content = pdf_reader.extract_text(file_path)
        
        if not text_content.strip():
            raise Exception("No text content found in PDF")
        
        print(f"✅ Text extracted: {len(text_content)} characters")
        
        # Step 2: Extract medicines using AI agent
        extraction_agent = MedicineExtractionAgent()
        medicines_json = extraction_agent.extract_medicines(text_content)
        
        # Parse the JSON result
        try:
            print(f"🔍 Parsing medicines JSON: {medicines_json[:200]}...")
            medicines_data = json.loads(medicines_json)
            medicines = medicines_data.get("medicines", [])
            print(f"✅ Found {len(medicines)} medicines in extraction result")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw medicines_json: {medicines_json}")
            medicines = []
        
        if not medicines:
            return {
                "medicines": [],
                "summary": {
                    "total_medicines": 0,
                    "medicines_with_alternatives": 0,
                    "total_alternatives_found": 0
                }
            }
        
        print(f"✅ Found {len(medicines)} medicines")
        
        # Step 3: Check if database exists
        if not os.path.exists("data/medicines.db"):
            raise Exception("Medicine database not found. Please create it first.")
        
        # Step 4: Find alternatives using AI agent
        alternative_agent = AlternativeSuggestionAgent()
        input_json = json.dumps({"medicines": medicines})
        alternatives_result = alternative_agent.suggest_alternatives(input_json)
        
        # Parse the alternatives result
        try:
            print(f"🔍 Parsing alternatives JSON: {alternatives_result[:200]}...")
            alternatives_data = json.loads(alternatives_result)
            print(f"✅ Alternatives data parsed successfully")
        except json.JSONDecodeError as e:
            print(f"❌ Alternatives JSON decode error: {e}")
            print(f"Raw alternatives_result: {alternatives_result}")
            raise Exception(f"Failed to parse alternatives result: {e}")
        
        if "error" in alternatives_data:
            raise Exception(f"Alternative suggestion error: {alternatives_data['error']}")
        
        print(f"✅ Processing completed successfully")
        return alternatives_data
        
    except Exception as e:
        print(f"❌ Error processing prescription: {e}")
        raise e

@app.post("/api/process-prescription")
async def process_prescription(prescription: UploadFile = File(...)):
    """
    Process uploaded prescription file and return medicine alternatives.
    """
    print(f"🔍 Received file upload: {prescription.filename}")
    print(f"📄 Content type: {prescription.content_type}")
    print(f"📏 File size: {prescription.size}")
    
    try:
        # Validate file type
        if prescription.content_type not in ["application/pdf", "image/jpeg", "image/png", "image/jpg"]:
            print(f"❌ Invalid file type: {prescription.content_type}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload PDF, JPEG, or PNG files only."
            )
        
        # Create temporary file
        print(f"📁 Creating temporary file...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await prescription.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        print(f"💾 Temporary file created: {tmp_file_path}")
        
        try:
            # Process the file
            print(f"🔄 Starting file processing...")
            result = process_prescription_file(tmp_file_path)
            print(f"✅ Processing completed, returning result")
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except HTTPException as e:
        print(f"❌ HTTP Exception: {e.detail}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error in API endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Medicine Alternative API is running"}

@app.post("/api/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload endpoint."""
    print(f"🧪 Test upload received: {file.filename}, {file.content_type}, {file.size}")
    return {
        "message": "File received successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size
    }

# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_dist = Path("generic-saver-bot/dist")
    if frontend_dist.exists():
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    
    return {"message": "Medicine Alternative API", "frontend": "not built yet"}

@app.get("/{path:path}")
async def serve_frontend_routes(path: str):
    """Serve frontend routes for SPA."""
    frontend_dist = Path("generic-saver-bot/dist")
    if frontend_dist.exists():
        # Try to serve the specific file
        file_path = frontend_dist / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Fallback to index.html for SPA routing
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    
    raise HTTPException(status_code=404, detail="File not found")

# ============================================================================
# NEW FUZZY SEARCH ENDPOINTS (Safe additions - don't affect existing functionality)
# ============================================================================

@app.get("/api/search/fuzzy/{medicine_name}")
async def search_medicine_fuzzy_endpoint(medicine_name: str, limit: int = 5):
    """
    NEW: Fuzzy search for medicine names (handles typos and variations).
    This endpoint is ADDITIONAL to existing functionality.
    
    Args:
        medicine_name (str): Medicine name to search (can have typos)
        limit (int): Maximum number of results to return
    
    Returns:
        Dict: Search results with similarity scores and suggestions
    """
    try:
        # Use the new fuzzy search functionality
        results = search_medicine_fuzzy(medicine_name, limit)
        
        return {
            "success": True,
            "query": medicine_name,
            "results": results,
            "search_type": "fuzzy"
        }
        
    except Exception as e:
        print(f"❌ Error in fuzzy search: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": medicine_name,
            "search_type": "fuzzy"
        }

@app.get("/api/search/suggestions/{partial_name}")
async def get_medicine_suggestions(partial_name: str, limit: int = 10):
    """
    NEW: Get medicine name suggestions for autocomplete.
    This endpoint is ADDITIONAL to existing functionality.
    
    Args:
        partial_name (str): Partial medicine name
        limit (int): Maximum suggestions to return
        
    Returns:
        List[str]: List of suggested medicine names
    """
    try:
        if len(partial_name) < 2:
            return {
                "success": True,
                "query": partial_name,
                "suggestions": [],
                "message": "Query too short for suggestions"
            }
        
        searcher = FuzzyMedicineSearch()
        suggestions = searcher.get_suggestions(partial_name, limit)
        
        return {
            "success": True,
            "query": partial_name,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        print(f"❌ Error getting suggestions: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": partial_name,
            "suggestions": []
        }

@app.get("/api/search/enhanced/{medicine_name}")
async def search_medicine_enhanced(medicine_name: str, limit: int = 5):
    """
    NEW: Enhanced search combining exact + fuzzy matching.
    This endpoint is ADDITIONAL to existing functionality.
    
    Args:
        medicine_name (str): Medicine name to search
        limit (int): Maximum results
        
    Returns:
        Dict: Enhanced search results with confidence levels
    """
    try:
        searcher = FuzzyMedicineSearch()
        results = searcher.search_with_suggestions(medicine_name, limit)
        
        return {
            "success": True,
            "query": medicine_name,
            "results": results,
            "search_type": "enhanced"
        }
        
    except Exception as e:
        print(f"❌ Error in enhanced search: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": medicine_name,
            "search_type": "enhanced"
        }

# ============================================================================
# END OF NEW FUZZY SEARCH ENDPOINTS
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Medicine Alternative API...")
    print("📊 Frontend will be available at: http://localhost:8001")
    print("🔗 API endpoints at: http://localhost:8001/api/")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 