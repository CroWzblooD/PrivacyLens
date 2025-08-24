# PrivacyLens Backend

Professional modular backend for PII detection and redaction using FastAPI.

## Features

- 🔍 **Advanced PII Detection**: Multi-pattern detection with AI validation
- 🤖 **LLM Integration**: GROQ API for intelligent content analysis
- 📄 **PDF Processing**: Multi-page PDF support with OCR capabilities
- 🎨 **Smart Redaction**: Context-aware redaction with different techniques
- 🚀 **FastAPI Backend**: Modern async API with automatic documentation
- 📊 **Real-time Progress**: Background job processing with live updates
- 🔧 **Modular Architecture**: Clean, maintainable, and extensible code

## Architecture

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Configuration and settings
│   ├── models/        # Data models and schemas
│   ├── services/      # Business logic services
│   └── utils/         # Helper utilities
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

## Services

- **OCR Service**: Text extraction from scanned documents
- **PII Detection**: Pattern-based and AI-enhanced detection
- **LLM Agent**: GROQ API integration for smart validation
- **Coordinate Mapper**: Text-to-coordinate mapping with validation
- **Redaction Engine**: Multi-technique redaction application
- **Image Detection**: Detection and classification of images
- **Job Manager**: Background task management and progress tracking

## Installation

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Install Tesseract OCR** (for scanned documents):
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

3. **Configure settings** (optional):
   - Edit `app/core/config.py` for custom configuration
   - Update GROQ API key if needed

## Usage

### Start the server:
```bash
cd backend
python main.py
```

The server will start on `http://localhost:8001`

### API Endpoints:

- **POST /api/upload** - Upload PDF for processing
- **GET /api/status/{job_id}** - Get processing status
- **GET /api/download/{job_id}** - Download processed file
- **GET /api/health** - Health check
- **GET /docs** - Interactive API documentation

### Example Usage:

```python
import requests

# Upload a file
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8001/api/upload",
        files={"file": f}
    )
    job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8001/api/status/{job_id}")
print(status.json())

# Download result when completed
if status.json()["status"] == "completed":
    result = requests.get(f"http://localhost:8001/api/download/{job_id}")
    with open("redacted.pdf", "wb") as f:
        f.write(result.content)
```

## Configuration

Key configuration options in `app/core/config.py`:

- **PORT**: Server port (default: 8001)
- **GROQ_API_KEY**: GROQ API key for LLM validation
- **TESSERACT_PATH**: Path to Tesseract executable
- **MAX_FILE_SIZE**: Maximum upload file size
- **PDF_SCALE_FACTOR**: PDF to image scaling factor

## Development

### Adding New PII Patterns:
Edit `app/services/pii_detection.py` and update the `enhanced_patterns` dictionary.

### Adding New Services:
1. Create new service in `app/services/`
2. Import and initialize in `app/services/pii_processor.py`
3. Add routes in `app/api/routes.py` if needed

### Testing:
```bash
pytest
```

## Troubleshooting

1. **Tesseract not found**: Install Tesseract OCR and update path in config
2. **GROQ API errors**: Check API key and internet connection
3. **File upload errors**: Check file size limits and permissions
4. **Import errors**: Ensure all dependencies are installed

## Performance Notes

- Processing time depends on document size and complexity
- OCR is used only for scanned documents (slower)
- LLM validation adds ~100ms per detection
- Multi-page documents are processed sequentially

## Security Considerations

- Uploaded files are stored temporarily
- GROQ API key should be kept secure
- Consider implementing authentication for production use
- Files are not automatically cleaned up (implement cleanup as needed)
