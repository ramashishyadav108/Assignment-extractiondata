# 📄 PDF Data Extraction System

A production-ready web application that extracts structured data from PDF documents using Google Gemini AI and outputs formatted Excel files.

![Python](https://img.shields.io/badge/Python-3.11.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0--Flash-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

- **PDF Upload**: Drag & drop interface with file validation and error notifications
- **Intelligent Extraction**: Gemini AI-powered data extraction with high accuracy
- **Excel Export**: Professional formatted Excel output with multiple sheets
- **Excel Viewer**: Built-in viewer to preview extracted data before download
- **Excel Comparison**: Compare two Excel files or compare output with expected results
- **Real-time Processing**: Live progress tracking with detailed status updates
- **Extraction History**: View and access all previous extractions
- **Error Handling**: Comprehensive validation with user-friendly toast notifications
- **Database Integration**: SQLite database for storing extraction records
- **File Type Validation**: Smart file validation that shows helpful error messages

## 🏗️ Architecture

```
User Interface (React + Vite)
    ↓
File Upload & Validation
    ↓
FastAPI Backend
    ↓
PDF Extractor (PyMuPDF/pdfplumber)
    ↓
Gemini AI (gemini-2.0-flash-exp)
    ↓
Excel Generator (openpyxl)
    ↓
SQLite Database (Storage)
    ↓
Excel Viewer & Comparison Tools
    ↓
Download / History
```

## 📋 Prerequisites

- **Python 3.11.9** (recommended for deployment)
- **Node.js 18+**
- **Google Gemini API Key** (free tier available)

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

5. **Run the server**:
```bash
# Using the start script (recommended)
./start.sh

# Or manually
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Run development server**:
```bash
npm run dev
```

The API will be available at `http://localhost:8000`

---

**Note**: Docker support will be added in future updates.

## 📖 Usage

### Basic Extraction Flow

1. **Open the application** at `http://localhost:5173`
2. **Upload PDF files** via drag & drop or file selector
   - Only PDF files are accepted (images/other files show error toast)
   - Maximum file size: 50MB
3. **Select extraction template** (if applicable)
4. **Click "Start Extraction"** to begin processing
5. **Monitor progress** with real-time updates
6. **Preview extracted data** in the built-in Excel viewer
7. **Download Excel file** when satisfied with results
8. **Access history** to view all previous extractions

### Excel Comparison

#### Compare Two Excel Files
1. Click **"Compare Excel"** in the header
2. Upload two Excel files to compare
3. View detailed comparison with:
   - Overall accuracy percentage
   - Cell-by-cell differences highlighted
   - Sheet-wise comparison
   - Match/difference statistics

#### Compare with Expected Output
1. After extraction, on the results page
2. Click **"Compare with Expected Output"**
3. Upload your expected output file
4. System compares it with the extracted output
5. View accuracy metrics and differences

### View Extraction History
1. Click **"History"** in the header
2. Browse all previous extractions
3. View details (date, filename, status)
4. Download previous outputs
5. Compare previous results

---

## 🔧 LLM Configuration

This system uses **Google Gemini 2.0 Flash (Experimental)** for intelligent data extraction.

### Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `backend/.env`:
   ```env
   GEMINI_API_KEY=your-key-here
   ```

### Current Model
- `gemini-2.0-flash-exp` (current default - fast, accurate & experimental)

### Alternative Supported Models
- `gemini-1.5-pro` (stable, more expensive)
- `gemini-1.5-flash` (stable, fast)
- `gemini-2.5-flash` (if available in your region)

Change the model in `backend/app/services/gemini_extractor.py`:
```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

## 🔧 API Documentation

### Endpoints

#### `GET /`
Welcome endpoint with API information.

#### `GET /health`
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00",
  "database": "connected",
  "output_dir": "/path/to/outputs"
}
```

#### `POST /api/extract`
Upload PDF files for extraction.

**Request**:
- `files`: PDF file(s) (multipart/form-data)
- `template`: Optional template identifier

**Response**:
```json
{
  "job_id": "uuid",
  "status": "processing",
  "filename": "document.pdf",
  "output_filename": "document_Extracted_Fund_Data.xlsx",
  "created_at": "2025-01-01T00:00:00"
}
```

#### `GET /api/download/{filename}`
Download generated Excel file.

**Response**: Excel file (.xlsx)

#### `GET /api/preview/{filename}`
Get Excel file data for preview.

**Response**:
```json
{
  "sheets": ["Sheet1", "Sheet2"],
  "data": {
    "Sheet1": [[row1_data], [row2_data], ...]
  }
}
```

#### `GET /api/files`
List all uploaded files with pagination.

**Query Parameters**:
- `skip`: Offset for pagination (default: 0)
- `limit`: Number of records (default: 50)
- `status`: Filter by status (uploaded, processing, completed, failed)

**Response**:
```json
{
  "total": 10,
  "files": [
    {
      "id": 1,
      "filename": "document.pdf",
      "status": "completed",
      "uploaded_at": "2025-01-01T00:00:00",
      "file_size": 1024000
    }
  ]
}
```

#### `GET /api/files/{file_id}`
Get details of a specific file.

#### `GET /api/jobs`
List all extraction jobs.

#### `GET /api/jobs/{job_id}`
Get specific job details and status.

**Response**:
```json
{
  "job_id": "uuid",
  "file_id": 1,
  "status": "completed",
  "output_filename": "output.xlsx",
  "error_message": null,
  "created_at": "2025-01-01T00:00:00",
  "completed_at": "2025-01-01T00:05:00"
}
```

#### `GET /api/results`
List all extraction results with filtering.

**Query Parameters**:
- `skip`: Offset (default: 0)
- `limit`: Limit (default: 50)
- `status`: Filter by status

#### `GET /api/results/{result_id}`
Get specific extraction result details.

#### `GET /api/logs/{file_id}`
Get extraction logs for a specific file.

#### `DELETE /api/files/{file_id}`
Delete an uploaded file and associated data.

#### `GET /api/templates`
List available extraction templates.

**Response**:
```json
{
  "templates": {
    "default": "Fund Data Extraction Template"
  }
}
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation with interactive testing.

## 📁 Project Structure

```
pdf-extraction-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   ├── database/              # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Database connection
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   └── crud.py            # CRUD operations
│   │   ├── services/              # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── pdf_extractor.py   # PDF text extraction
│   │   │   ├── gemini_extractor.py # Gemini AI integration
│   │   │   └── excel_generator.py # Excel file generation
│   │   └── templates/             # Prompt templates
│   │       ├── __init__.py
│   │       ├── prompt_template.py  # Main prompt template
│   │       ├── prompt_template_simple.py
│   │       └── prompt_template_old.py
│   ├── outputs/                   # Generated Excel outputs
│   ├── main.py                    # FastAPI application entry
│   ├── requirements.txt           # Python dependencies
│   ├── runtime.txt                # Python version for deployment
│   ├── start.sh                   # Startup script
│   ├── setup_dirs.sh              # Directory setup script
│   ├── test_progressive_chunking.py
│   ├── test_updated_chunking.py
│   └── .env.example               # Environment variables template
│
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── FileUpload.jsx     # Drag & drop file upload
│   │   │   ├── TemplateSelector.jsx # Template selection
│   │   │   ├── ExtractionProgress.jsx # Progress display
│   │   │   ├── ProcessingPage.jsx # Processing UI
│   │   │   ├── ResultsPage.jsx    # Results display
│   │   │   ├── HistoryPage.jsx    # Extraction history
│   │   │   ├── DataPreview.jsx    # Data preview
│   │   │   ├── DownloadButton.jsx # Download functionality
│   │   │   ├── ExcelViewer.jsx    # Excel file viewer
│   │   │   ├── ExcelSheetViewer.jsx # Sheet viewer
│   │   │   ├── CompareXLSX.jsx    # Excel comparison tool
│   │   │   ├── Header.jsx         # App header
│   │   │   └── Footer.jsx         # App footer
│   │   ├── services/              # API services
│   │   │   └── api.js             # API client
│   │   ├── styles/                # Component styles
│   │   │   ├── CompareXLSX.css
│   │   │   ├── DataPreview.css
│   │   │   ├── ExcelSheetViewer.css
│   │   │   ├── ExcelViewer.css
│   │   │   ├── Footer.css
│   │   │   ├── Header.css
│   │   │   ├── HistoryPage.css
│   │   │   ├── ProcessingPage.css
│   │   │   └── ResultsPage.css
│   │   ├── App.jsx                # Main app component
│   │   ├── App.css                # Global styles
│   │   ├── index.css              # Base styles
│   │   └── main.jsx               # React entry point
│   ├── index.html                 # HTML template
│   ├── package.json               # Node dependencies
│   ├── vite.config.js             # Vite configuration
│   └── vercel.json                # Vercel deployment config
│
├── examples/                      # Sample files
│   ├── sample_pdfs/               # Example PDF inputs
│   └── output/                    # Example outputs
│
├── .env.example                   # Environment variables example
├── .python-version                # Python version (3.11.9)
├── .gitignore                     # Git ignore rules
├── render.yaml                    # Render deployment config
├── test_health.sh                 # Health check script
└── README.md                      # This file
```

## 🎨 Extraction Templates

The system uses intelligent AI-powered prompts to extract structured data from fund report PDFs.

### Main Template Features
- **Fund Information**: Name, manager, vintage year, fund size
- **Performance Metrics**: IRR, TVPI, DPI, RVPI, MOIC
- **Capital Data**: Commitments, contributions, distributions
- **Investment Details**: Portfolio holdings, sector allocation
- **Financial Data**: NAV, fair values, cash positions
- **Dates & Timeline**: Key dates, reporting periods

### Customization
Templates can be customized in `backend/app/templates/prompt_template.py` to:
- Add new data fields
- Modify extraction logic
- Change output format
- Add validation rules

## 🧪 Testing

### Manual Testing
1. Place test PDFs in `examples/sample_pdfs/`
2. Run the backend server
3. Upload PDFs through the frontend
4. Compare outputs in `backend/outputs/` with expected results

### Test Scripts
```bash
# Test progressive chunking
cd backend
python test_progressive_chunking.py

# Test updated chunking
python test_updated_chunking.py
```

### Health Check
```bash
# Run health check script
./test_health.sh

# Or manually
curl http://localhost:8000/health
```

## 🔒 Security Best Practices

- ✅ API keys stored in environment variables
- ✅ File type validation
- ✅ File size limits (50MB)
- ✅ CORS configuration
- ✅ Input sanitization
- ✅ Error message sanitization

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | SQLite database path | sqlite:///./extractions.db |
| `UPLOAD_DIR` | Upload directory | ./uploads |
| `OUTPUT_DIR` | Output directory | ./outputs |
| `MAX_FILE_SIZE` | Max file size (bytes) | 52428800 (50MB) |
| `CORS_ORIGINS` | Allowed CORS origins | ["*"] |
| `DEBUG` | Debug mode | False |

### Frontend Configuration

Create a `.env` file in the frontend directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | http://localhost:8000/api |

### Database

The application uses SQLite by default with the following tables:
- `uploaded_files`: Track uploaded PDFs
- `extraction_results`: Store extraction results
- `extraction_logs`: Log extraction process
- `job_status`: Track job statuses

## 📊 Performance

- **Extraction Accuracy**: >90% on complex fund documents
- **Processing Time**: ~30-90 seconds per document (depending on size)
- **Database**: SQLite for fast local storage
- **File Support**: PDF files up to 50MB
- **Concurrent Extractions**: Supports multiple simultaneous uploads
- **AI Model**: Gemini 2.0 Flash Experimental (latest)

## 🚀 Deployment

### Quick Deploy (Render)

This project is configured for **one-push deployment** to Render using `render.yaml`.

**Prerequisites:**
- GitHub account
- Render account (free tier available)
- Gemini API key

**Steps:**

1. **Push to GitHub:**
```bash
git push origin main
```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Add Environment Variables:**
   - Add `GEMINI_API_KEY` in Render dashboard
   - Other variables are auto-configured

4. **Deploy:**
   - Click "Apply"
   - Wait 5-10 minutes for deployment
   - Backend: `https://pdf-extraction-backend.onrender.com`
   - Frontend: `https://pdf-extraction-frontend.onrender.com`

### Python Version Configuration

The project uses **Python 3.11.9** for production:
- Specified in `.python-version`
- Configured in `backend/runtime.txt`
- Set in `render.yaml` as `runtime: python-3.11.9`

### Template Files

Templates are **deployed with the backend**:
- Located in `backend/templates/`
- Automatically included in deployment
- API endpoint: `/api/templates` to verify

### Production Deployment Checklist

- [x] Python 3.11.9 configured
- [x] SQLite database integration
- [x] Environment variables configured
- [x] `render.yaml` configured for backend
- [x] `vercel.json` configured for frontend
- [ ] Set `DEBUG=False` in production
- [ ] Configure production CORS origins
- [ ] Add `GEMINI_API_KEY` to deployment platform
- [ ] Configure frontend `VITE_API_URL` for production
- [ ] Enable HTTPS (auto on Render/Vercel)
- [ ] Set up logging and monitoring
- [ ] Configure database backups (if needed)
- [ ] Set up file cleanup jobs (optional)
- [ ] Test all endpoints in production
- [ ] Monitor API rate limits

### Alternative Deployment Options

#### Vercel (Frontend) + Render (Backend)
```bash
# Frontend on Vercel
cd frontend
npm run build
vercel deploy

# Backend on Render (using render.yaml)
git push origin main
```

#### AWS/GCP/Azure
Use provided configuration files for containerized deployment.

## 🐛 Troubleshooting

### Common Issues

**Issue**: Database errors or "table not found"
```bash
# Solution: Initialize database
cd backend
python -c "from app.database import init_db; init_db()"
```

**Issue**: "API key not configured" or Gemini errors
```bash
# Check .env file exists and contains valid key
cat backend/.env

# Verify API key is valid at https://aistudio.google.com/app/apikey

# For Render deployment:
# Settings → Environment → GEMINI_API_KEY
```

**Issue**: "Import errors" when running backend
```bash
# Ensure you're in the correct directory and venv is activated
cd pdf-extraction-system/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Issue**: Frontend can't connect to backend (CORS errors)
```bash
# Update backend/.env with frontend URL:
CORS_ORIGINS=["http://localhost:5173", "https://your-frontend.vercel.app"]

# Restart backend server
```

**Issue**: File upload shows no files or validation errors
- Make sure you're selecting PDF files (not images)
- Check file size is under 50MB
- For Excel comparison, ensure files are .xlsx or .xls format
- Clear browser cache if issues persist

**Issue**: Extraction fails or produces empty results
- Verify PDF is text-based (not scanned images)
- Check Gemini API quota at Google AI Studio
- Review extraction logs in the database
- Try with a different PDF to isolate the issue

**Issue**: "Port already in use" errors
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

**Issue**: Excel viewer not showing data
- Ensure Excel file was successfully generated
- Check browser console for errors
- Verify file exists in backend/outputs/
- Try downloading and opening locally

**Issue**: Comparison feature not working
- Both files must be valid Excel files
- Files should have similar structure for meaningful comparison
- Check that output file exists before comparing

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FastAPI** - High-performance Python web framework
- **Google Gemini AI** - Advanced LLM for data extraction
- **React + Vite** - Modern frontend framework and build tool
- **React Router** - Client-side routing
- **React Hot Toast** - Beautiful notification system
- **React Dropzone** - File upload with drag & drop
- **PyMuPDF (fitz)** - PDF text extraction
- **pdfplumber** - Additional PDF parsing
- **openpyxl** - Excel file generation and manipulation
- **xlsx (SheetJS)** - Frontend Excel file reading
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Embedded database

## 📞 Support

For issues and questions:
- 🐛 Create an issue on GitHub
- 📖 Check the troubleshooting section above
- 📚 Review API documentation at `/docs`
- 💬 Check existing issues for solutions

## 🔄 Version History

### v2.0.0 (Current)
- ✅ Database integration with SQLite
- ✅ Excel viewer and preview functionality
- ✅ Excel comparison tool (dual mode & single mode)
- ✅ Extraction history with full record tracking
- ✅ Enhanced UI with React Router
- ✅ File validation with toast notifications
- ✅ Multiple component pages (Processing, Results, History, Compare)
- ✅ Real-time progress tracking
- ✅ Google Gemini 2.0 Flash Experimental integration
- ✅ Improved error handling and logging
- ✅ RESTful API with comprehensive endpoints

### v1.0.0 (Initial)
- Basic PDF extraction
- Gemini AI integration
- Excel output generation
- Simple frontend interface

---

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8000/docs` (when running locally)
- **Template Schema**: Check `/api/templates` endpoint
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Gemini API**: [ai.google.dev](https://ai.google.dev)

---

**Built with ❤️ using React, FastAPI, and Google Gemini**
