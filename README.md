# Multilingual Legal Document Summarization Tool for District Court E-Services

## Overview
An AI-powered backend service designed to process, parse, chunk, summarize, and translate complex legal documents used in Indian District Court e-Services.

Currently implemented: **Stages 1 - 5 (Backend AI Pipeline & Pan-Indian Multilingual Support)** & **Stage 7 (Professional Report Export in PDF, DOCX, TXT)**.

---

## Features
- **Document Parsing API**: Fast, reliable text extraction from PDF and DOCX documents via `POST /upload`.
- **PyMuPDF & Python-Docx Parsers**: Page-by-page PDF processing with error resilience for unreadable or encrypted pages.
- **Intelligent Chunking Engine**: Context-aware legal text chunking with overlap management.
- **Gemini AI Legal Summarizer**: Powered by Gemini 2.5 Flash Lite with exponential backoff retries.
- **Pan-Indian Multilingual Support**: Supports 7 languages: **English, Tamil, Hindi, Telugu, Kannada, Malayalam, and Marathi**.
- **Professional Report Export (Stage 7)**:
  - **PDF Export**: Built with ReportLab using custom page templates, header banners, metadata tables, dynamic footers ("Page X of Y"), and Indic Unicode font rendering.
  - **DOCX Export**: Structured Word document built with `python-docx` using heading hierarchies, metadata cards, and styled typography.
  - **TXT Export**: Clean UTF-8 encoded plain text report.
  - Dynamic in-memory file generation & streaming (no permanent storage).

---

## Tech Stack
- **Language**: Python 3.12+
- **Web Framework**: FastAPI, Uvicorn
- **Parsing Libraries**: PyMuPDF (`fitz`), `python-docx`
- **PDF Generation**: ReportLab (`reportlab>=4.0.0`)
- **Frontend Stack**: React, Vite, Tailwind CSS, Framer Motion, Lucide Icons
- **Validation & Settings**: Pydantic, `pydantic-settings`

---

## Project Structure
```text
backend/
├── app/
│   ├── main.py              # FastAPI application entry point & error handlers
│   ├── config.py            # Application settings and environment variables
│   ├── routers/
│   │   └── upload.py        # File upload and processing endpoint
│   ├── schemas/
│   │   └── upload.py        # Pydantic request/response schemas
│   ├── services/
│   │   ├── parser.py        # PDF & DOCX text extraction logic
│   │   └── chunking.py      # Independent text chunking utilities (Stage 2 preparation)
│   ├── utils/
│   │   └── token_estimator.py # Lightweight token estimation utility
│   └── core/                # Core system utilities / shared modules
├── uploads/                 # Storage directory for temporary upload files
├── requirements.txt         # Project dependencies
├── .env.example             # Template for environment variables
├── .gitignore               # Git ignore file
└── README.md                # Documentation
```

---

## Getting Started

### Prerequisites
- Python 3.12 or higher
- `pip` package manager

### 1. Environment Setup
Create and activate a virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run the Development Server
```bash
uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

Interactive API documentation (Swagger UI) is available at:
`http://127.0.0.1:8000/docs`

---

## API Documentation

### POST `/summarize`

Accepts a multipart file upload (`.pdf` or `.docx`) and returns a multilingual legal summary.

#### Supported Languages
- `en` for English
- `ta` for Tamil
- `hi` for Hindi
- `te` for Telugu
- `kn` for Kannada
- `ml` for Malayalam
- `mr` for Marathi
- `auto` for automatic source-language detection

#### Request Parameters
- `file`: uploaded document
- `source_language`: optional, one of `auto`, `en`, `ta`
- `target_language`: required, one of `en`, `ta`

#### Example Curl Request
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/summarize' \
  -H 'accept: application/json' \
  -F 'file=@judgement.pdf;type=application/pdf' \
  -F 'source_language=auto' \
  -F 'target_language=ta'
```

#### Translation Workflow
- English document → English summary → Tamil summary when `target_language=ta`
- Tamil document → Tamil summary → English summary when `target_language=en`
- The system avoids translating the full document when a summary-only translation is sufficient.

#### Language Detection Behavior
- English and Tamil are detected using lightweight heuristics.
- Mixed-language content returns a clear validation error.
- Unsupported values for `source_language` or `target_language` return a `400` response.

### POST `/upload`

Accepts a multipart file upload (`.pdf` or `.docx`), extracts the raw text, and returns the response metadata.

#### Request
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (Binary file, max 100 MB)

#### Example Curl Request
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@judgement.pdf;type=application/pdf'
```

#### Successful Response (`200 OK`)
```json
{
  "filename": "judgement.pdf",
  "pages": 18,
  "text": "IN THE COURT OF THE DISTRICT JUDGE...\n\nParagraph 1 text..."
}
```

#### Error Responses
- **`400 Bad Request`**:
  - Unsupported file type (only `.pdf` and `.docx` are allowed)
  - Empty file upload
  - File size exceeds maximum limit (100 MB)
  - Password-protected PDF
  - Corrupted PDF or invalid DOCX document

---

## Demo Login Credentials (Stage 6)
To log into the District Court e-Services Workspace:
- **Email:** `advocate@ecourt.gov`
- **Password:** `Password@123`
- **Role:** Advocate
- **Name:** Advocate Ramesh

To start the applications:
```bash
# Terminal 1: Backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## Development Roadmap
- [x] **Stage 1**: Document parsing, validation, chunking scaffolding, and `/upload` endpoint.
- [x] **Stage 2**: Text cleaning, legal pre-processing, and Chunking Engine integration.
- [x] **Stage 3**: Gemini LLM summarization pipeline integration.
- [x] **Stage 4**: Multilingual translation support.
- [x] **Stage 5**: Backend AI Pipeline & Pan-Indian Multilingual Support.
- [x] **Stage 6**: Frontend Integration and UI Enhancements.
- [x] **Stage 7**: Professional Report Export in PDF, DOCX, TXT.
