"""
Core configuration settings for PrivacyLens Backend
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    RELOAD: bool = True
    
    # API Configuration
    API_TITLE: str = "PrivacyLens API"
    API_DESCRIPTION: str = "Advanced PII Detection and Redaction"
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Tesseract OCR Configuration
    TESSERACT_PATH: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # GROQ API Configuration
    GROQ_API_KEY: str = "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"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TIMEOUT: int = 5
    
    # Processing Configuration
    PDF_SCALE_FACTOR: float = 2.0
    OCR_CONFIDENCE_THRESHOLD: int = 30
    
    def __init__(self):
        # Create necessary directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        
        # Setup Tesseract path if on Windows
        if os.name == 'nt' and os.path.exists(self.TESSERACT_PATH):
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_PATH

# Global settings instance
settings = Settings()