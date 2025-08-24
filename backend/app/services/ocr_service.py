"""
OCR Service for text extraction from images and PDFs
"""

import io
import fitz
import pytesseract
from PIL import Image
from typing import List, Tuple, Optional
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service for text extraction"""
    
    def __init__(self):
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
        logger.info("OCR Service initialized")
    
    def extract_text_from_page(self, page) -> Tuple[List, str]:
        """Extract text from a PDF page using OCR"""
        try:
            logger.debug("Converting PDF page to image for OCR")
            mat = fitz.Matrix(settings.PDF_SCALE_FACTOR, settings.PDF_SCALE_FACTOR)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            logger.debug("Running Tesseract OCR")
            ocr_text = pytesseract.image_to_string(img)
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            words = []
            for i in range(len(ocr_data["text"])):
                word = ocr_data["text"][i].strip()
                if word and ocr_data["conf"][i] > self.confidence_threshold:
                    x = ocr_data["left"][i] / settings.PDF_SCALE_FACTOR
                    y = ocr_data["top"][i] / settings.PDF_SCALE_FACTOR
                    w = ocr_data["width"][i] / settings.PDF_SCALE_FACTOR
                    h = ocr_data["height"][i] / settings.PDF_SCALE_FACTOR
                    words.append([x, y, x + w, y + h, word])
            
            return words, ocr_text
            
        except ImportError:
            logger.warning("Tesseract not available, cannot OCR document")
            return [], ""
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return [], ""
    
    def is_scanned_document(self, page) -> bool:
        """Check if a page is a scanned document"""
        try:
            text = page.get_text().strip()
            words = page.get_text("words")
            return len(text) == 0 or len(words) == 0
        except Exception as e:
            logger.error(f"Error checking if document is scanned: {e}")
            return False
