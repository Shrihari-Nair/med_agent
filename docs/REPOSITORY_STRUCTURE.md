# Repository Structure

This document describes the organized structure of the Medicine Alternative System.

## 📁 **New Repository Organization**

```
med_agent/
├── 📁 src/                           # Source code
│   ├── agents/                       # AI Agents
│   │   ├── __init__.py
│   │   ├── medicine_agent.py         # Medicine extraction agent (with fuzzy search)
│   │   └── alternative_suggestion_agent.py  # Alternative suggestion agent
│   ├── database/                     # Database management
│   │   ├── __init__.py
│   │   ├── manager.py               # Database manager (was medicine_database_manager.py)
│   │   ├── create_db.py            # Database creation (was create_medicine_db.py)
│   │   └── view_db.py              # Database viewer (was view_medicine_db.py)
│   ├── api/                         # Backend API
│   │   ├── __init__.py
│   │   └── backend.py              # FastAPI backend (was backend_api.py)
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── pdf_reader.py           # PDF processing
│   │   ├── fuzzy_search.py         # Fuzzy medicine search (was fuzzy_medicine_search.py)
│   │   └── pipeline.py             # Main pipeline (was main_pipeline.py)
│   └── __init__.py
├── 📁 tests/                        # Test files
│   ├── __init__.py
│   ├── test_fuzzy_api.py           # Fuzzy search API tests
│   ├── test_backend.py             # Backend tests
│   └── test_actual_upload.py       # Upload functionality tests
├── 📁 scripts/                      # Startup and utility scripts
│   ├── start.py                    # Main startup script
│   ├── start.sh                    # Shell startup script
│   └── run_server.py               # Server runner
├── 📁 docs/                         # Documentation
│   ├── FUZZY_SEARCH.md            # Fuzzy search documentation
│   └── REPOSITORY_STRUCTURE.md    # This file
├── 📁 data/                         # Data files
│   ├── medicines.db               # Medicine database
│   ├── sample_prescription*.pdf   # Sample PDF files
│   ├── extracted_medicines.json  # Sample extracted data
│   └── medicine_alternatives.json # Sample alternatives data
├── 📁 frontend/                     # Frontend application
│   └── generic-saver-bot/         # React/Vite frontend
├── start.sh                        # Root-level startup script (backwards compatible)
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
└── .gitignore                     # Git ignore rules
```

## 🔄 **Import Path Changes**

### **Before Restructuring:**
```python
from medicine_agent import MedicineExtractionAgent
from alternative_suggestion_agent import AlternativeSuggestionAgent
from medicine_database_manager import MedicineDatabaseManager
from fuzzy_medicine_search import FuzzyMedicineSearch
from pdf_reader import PDFReader
```

### **After Restructuring:**
```python
from src.agents.medicine_agent import MedicineExtractionAgent
from src.agents.alternative_suggestion_agent import AlternativeSuggestionAgent
from src.database.manager import MedicineDatabaseManager
from src.utils.fuzzy_search import FuzzyMedicineSearch
from src.utils.pdf_reader import PDFReader
```

## 🚀 **How to Start the System**

### **Option 1: Root Level (Backwards Compatible)**
```bash
./start.sh
```

### **Option 2: Direct Script**
```bash
./scripts/start.sh
```

Both methods will:
1. ✅ Start the FastAPI backend on `http://localhost:8001`
2. ✅ Start the frontend on `http://localhost:8080`
3. ✅ Create the database if it doesn't exist
4. ✅ All existing functionality preserved

## 🧪 **Running Tests**

```bash
# Test fuzzy search API
python tests/test_fuzzy_api.py

# Test backend functionality
python tests/test_backend.py

# Test file upload
python tests/test_actual_upload.py
```

## 📦 **Key Benefits of New Structure**

### **1. Organized Code**
- ✅ **Agents**: All AI agents in one place
- ✅ **Database**: All database operations centralized
- ✅ **API**: Clean separation of API logic
- ✅ **Utils**: Reusable utilities organized
- ✅ **Tests**: All tests in dedicated folder

### **2. Better Maintainability**
- ✅ **Clear responsibilities**: Each module has a specific purpose
- ✅ **Easy navigation**: Find files quickly by category
- ✅ **Modular design**: Easy to add new features
- ✅ **Clean imports**: Explicit import paths

### **3. Backwards Compatibility**
- ✅ **Same startup command**: `./start.sh` still works
- ✅ **Same API endpoints**: All existing endpoints preserved
- ✅ **Same functionality**: No breaking changes
- ✅ **Enhanced features**: Fuzzy search now integrated

## 📋 **File Responsibilities**

| Category | Files | Purpose |
|----------|-------|---------|
| **Agents** | `src/agents/` | AI agents for medicine extraction and alternatives |
| **Database** | `src/database/` | Database creation, management, and viewing |
| **API** | `src/api/` | FastAPI backend with all endpoints |
| **Utils** | `src/utils/` | PDF reading, fuzzy search, pipeline logic |
| **Tests** | `tests/` | All test files for verification |
| **Scripts** | `scripts/` | Startup and utility scripts |
| **Data** | `data/` | Database files and sample data |
| **Docs** | `docs/` | Documentation files |
| **Frontend** | `frontend/` | React/Vite user interface |

## 🔧 **Development Workflow**

### **Adding New Features**
1. **Agent**: Add to `src/agents/`
2. **Database**: Add to `src/database/`
3. **API Endpoint**: Add to `src/api/backend.py`
4. **Utility**: Add to `src/utils/`
5. **Test**: Add to `tests/`

### **Database Path**
- **Old**: `medicines.db`
- **New**: `data/medicines.db`
- **Auto-handled**: All imports updated automatically

### **Import Strategy**
```python
# Always use full paths from project root
from src.module.file import ClassName

# Example
from src.agents.medicine_agent import MedicineExtractionAgent
```

## ✨ **New Features Included**

1. **🔍 Fuzzy Medicine Search**: Handles typos in medicine names
2. **📁 Organized Structure**: Better code organization
3. **🧪 Enhanced Testing**: Dedicated test structure
4. **📖 Better Documentation**: Comprehensive docs

## 🔄 **Migration Summary**

All files have been successfully reorganized with:
- ✅ **Updated import statements**
- ✅ **Corrected file paths**
- ✅ **Preserved functionality**
- ✅ **Enhanced structure**
- ✅ **Backwards compatibility**

The system is now more maintainable, organized, and ready for future enhancements! 