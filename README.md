# Medicine Extraction & Alternative Suggestion System

An AI-powered system that extracts medicine names and quantities from PDF prescriptions and suggests cost-effective alternatives using CrewAI and Google Gemini.

## ✨ Features

- 📄 **PDF Processing**: Extracts text from prescription PDFs using PyMuPDF
- 🤖 **AI Agents**: Two CrewAI agents with Gemini 2.0 Flash LLM
  - Medicine extraction agent for identifying medicines from text
  - Cost-saving alternative suggestion agent for finding cheaper options
- 💰 **Cost Optimization**: Suggests 3 cheapest alternatives with the same generic name
- 🗄️ **Database Integration**: SQLite database with 500 medicines across 20 classes
- 🌐 **Web Interface**: Modern React frontend with table view and statistics
- 🔗 **API Integration**: FastAPI backend serving the frontend
- 💾 **Comprehensive Results**: Shows per-unit and total savings with detailed medicine info

## 🚀 **Quick Start**

### **Option 1: One-Command Startup (Recommended)**
```bash
./start.sh
```

### **Option 2: Manual Setup**
```bash
# 1. Set your Gemini API key
export GOOGLE_API_KEY="your_gemini_api_key_here"

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the system
python start.py
```

### **Access the Application**
- **Frontend**: http://localhost:8080
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 **Requirements**

- **Python 3.8+**
- **Node.js 16+** and npm
- **Google Gemini API key** ([Get it here](https://makersuite.google.com/app/apikey))

## 🎯 **How It Works**

### **1. Upload Prescription**
- Upload PDF prescription via the web interface
- System extracts text using PyMuPDF

### **2. AI Medicine Extraction**
- Gemini AI identifies medicine names and quantities
- Returns structured JSON with medicine list

### **3. Alternative Suggestion**
- AI determines generic names for each medicine
- Database queries find cheaper alternatives with same generic
- Shows only alternatives that actually save money

### **4. Results Display**
- Interactive table showing all alternatives
- Per-unit and total savings calculations
- Detailed medicine information (manufacturer, class, stock)

## 💊 **Sample Output**

```
💊 Paracetamol - 10 tablets
   Generic: Acetaminophen
   Original Price: $12.50
   💰 Cost-effective alternatives:
      1. Acetaminophen Generic - $5.50
         Manufacturer: Generic Pharma
         Stock Available: 150 units
         Generic Name: Acetaminophen
         Therapeutic Class: Pain Relievers
         Per unit savings: $7.00 (56.0%)
         Total savings for 10 tablets: $70.00
```

## 🗄️ **Database**

The system includes a comprehensive medicine database with:
- **500 medicines** across **20 therapeutic classes**
- **Price variations** for cost comparison
- **Stock levels** for availability checking
- **Generic alternatives** for maximum savings
- **Manufacturer information**

### **Medicine Classes Include:**
Antibiotics, Pain Relievers, Antihistamines, Antacids, Antihypertensives, Antidiabetics, Statins, Antidepressants, Antipsychotics, Benzodiazepines, Corticosteroids, Anticoagulants, Diuretics, Bronchodilators, Antiemetics, Laxatives, Antifungals, Antivirals, Vitamins, Minerals

## 🔧 **Development**

### **File Structure**
```
med_agent/
├── start.sh                         # Quick startup script
├── start.py                         # Development server manager
├── backend_api.py                   # FastAPI server
├── main_pipeline.py                 # CLI pipeline (legacy)
├── pdf_reader.py                    # PDF text extraction
├── medicine_agent.py                # Medicine extraction agent
├── alternative_suggestion_agent.py  # Cost-saving alternatives agent
├── medicine_database_manager.py     # Database operations
├── create_medicine_db.py            # Database creation script
├── view_medicine_db.py              # Database viewer (optional)
├── requirements.txt                 # Python dependencies
├── generic-saver-bot/               # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md
```

### **API Endpoints**
- `POST /api/process-prescription` - Process prescription file
- `GET /api/health` - Health check
- `GET /` - Serve frontend application

### **Frontend Technology**
- **React 18** with TypeScript
- **Vite** build tool
- **Shadcn/UI** components
- **Tailwind CSS** for styling

## 🎛️ **Configuration**

### **Environment Variables**
```bash
GOOGLE_API_KEY="your_gemini_api_key"  # Required for AI processing
```

### **Alternative Selection Criteria**
The system finds medicines that:
✅ Same generic name (same active ingredient)
✅ Lower price than original
✅ Sufficient stock (≥10 units)
✅ Different medicine name (not just different brand)

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **"GOOGLE_API_KEY not set"**
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set environment variable: `export GOOGLE_API_KEY='your_key'`

2. **"npm not found"**
   - Install Node.js from [nodejs.org](https://nodejs.org/)

3. **"No alternatives found"**
   - Medicine might already be the cheapest option
   - Check if medicine exists in database with sufficient stock

4. **"Frontend not loading"**
   - Ensure both servers are running (port 8000 and 8080)
   - Check browser console for errors

## 🚦 **Production Deployment**

For production deployment:

1. **Build frontend**: `cd generic-saver-bot && npm run build`
2. **Start production server**: `python run_server.py`
3. **Access at**: http://localhost:8000

## 🔒 **Security Notes**

- File uploads are validated for type and size
- Temporary files are automatically cleaned up
- API includes CORS protection
- No sensitive data is stored

## 📊 **Performance**

- **Processing time**: 2-5 seconds per prescription
- **Database**: 500 medicines, sub-second queries
- **File support**: PDF, JPEG, PNG
- **Concurrent requests**: Supported via FastAPI

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test end-to-end functionality
5. Submit pull request

## 📄 **License**

This project is open source and available under the MIT License.

---

**🎉 Get started by running `./start.sh` and uploading a prescription PDF!** 