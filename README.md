# 📄 PDF Data Extraction System

AI-powered application that extracts structured data from PDF documents using Google Gemini AI and generates Excel files.

![Python](https://img.shields.io/badge/Python-3.11.9-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![React](https://img.shields.io/badge/React-18.2-blue) ![Gemini](https://img.shields.io/badge/Gemini-2.0--Flash-orange)

## 🎯 Features

- PDF upload with drag & drop
- AI-powered data extraction (Gemini 2.0)
- Excel file generation
- Built-in Excel viewer & comparison
- Extraction history with database
- Real-time progress tracking

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your-key" > .env
./start.sh
```
→ `http://localhost:8000`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
→ `http://localhost:5173`

## 📖 Usage

1. Open `http://localhost:5173`
2. Upload PDF files
3. Click "Start Extraction"
4. Preview & download Excel

## � Project Structure

```
pdf-extraction-system/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database/          
│   │   ├── services/          # PDF, Gemini, Excel
│   │   └── templates/         # Prompt templates
│   ├── outputs/               # Generated Excel files
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   ├── styles/            # CSS files
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── examples/                  # Sample PDFs & outputs
├── render.yaml
└── README.md
```

## �🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/extract` | Upload & extract PDF |
| GET | `/api/download/{filename}` | Download Excel |
| GET | `/api/files` | List files |
| GET | `/api/results` | List results |
| GET | `/health` | Health check |

**Docs:** `http://localhost:8000/docs`

## ⚙️ Configuration

**Backend `.env`:**
```env
GEMINI_API_KEY=your-key
DATABASE_URL=sqlite:///./extractions.db
MAX_FILE_SIZE=52428800
```

**Frontend `.env`:**
```env
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Deployment

**Render (Backend) + Vercel (Frontend)**
```bash
git push origin main
# Connect repos to Render & Vercel
# Set GEMINI_API_KEY on Render
# Set VITE_API_URL on Vercel
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Database errors | `python -c "from app.database import init_db; init_db()"` |
| API key missing | Check `.env` file |
| Port in use | `lsof -ti:8000 \| xargs kill -9` |
| CORS errors | Update `CORS_ORIGINS` in `.env` |

## 📊 Tech Stack

**Backend:** FastAPI, SQLAlchemy, SQLite, PyMuPDF  
**Frontend:** React, Vite, React Router  
**AI:** Google Gemini 2.0 Flash

---

**Built with ❤️ | [Get Gemini API Key](https://aistudio.google.com/app/apikey)**
