# Multilingual Legal Document Summarization Tool for District Court E-Services

## Overview
An AI-powered backend service designed to process, parse, chunk, summarize, and translate complex legal documents used in Indian District Court e-Services.

Currently implemented: **Stage 1 (Backend Core & Parsing Infrastructure)**.

---

## Features (Stage 1)
- **Document Parsing API**: Fast, reliable text extraction from PDF and DOCX documents via `POST /upload`.
- **PyMuPDF Parser**: Page-by-page PDF processing with error resilience for unreadable or corrupted pages.
- **Python-Docx Parser**: Clean paragraph extraction for Word documents.
- **Robust Validation**: File extension validation, maximum file size check (100 MB), empty file detection, corrupted file detection, and encrypted PDF detection.
- **Modular Architecture**: Clean architecture organized into routers, schemas, services, and utilities.
- **Chunking Scaffolding**: Prepared chunking and token estimation utilities for future AI pipeline stages.

---

## Tech Stack
- **Language**: Python 3.12+
- **Web Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Parsing Libraries**: PyMuPDF (`fitz`), `python-docx`
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

## Development Roadmap
- [x] **Stage 1 (Current)**: Document parsing, validation, chunking scaffolding, and `/upload` endpoint.
- [ ] **Stage 2**: Text cleaning, pre-processing, and Chunking Engine integration.
- [ ] **Stage 3**: Gemini LLM summarization pipeline integration.
- [ ] **Stage 4**: Multilingual translation (English ↔ Tamil).
- [ ] **Stage 5**: OCR support for scanned documents, PDF generation, persistence, and queue system.
