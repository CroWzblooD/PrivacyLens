"""
Redaction Engine Service for applying redactions to PDF documents
"""

import io
import os
import time
import fitz
from PIL import Image, ImageDraw, ImageFilter
from typing import List, Dict
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class RedactionEngineService:
    """Service for applying redactions to PDF documents"""
    
    def __init__(self):
        self.scale_factor = settings.PDF_SCALE_FACTOR
        logger.info("Redaction Engine Service initialized")
    
    def apply_redactions(self, doc, detections: List[Dict], output_path: str) -> Dict:
        """
        Apply redactions to a multi-page PDF document
        
        Args:
            doc: PyMuPDF document object
            detections: List of detection dictionaries
            output_path: Path to save redacted document
            
        Returns:
            Dictionary with redaction results
        """
        logger.info("Starting multi-page redaction process")
        
        if not detections:
            logger.warning("No detections to redact")
            return {"success": False, "message": "No detections to redact"}
        
        # Create a new PDF document for the redacted output
        new_doc = fitz.open()
        redaction_count = 0
        
        try:
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                logger.info(f"Processing page {page_num + 1}/{len(doc)} for redaction")
                
                # Get detections for this page only
                page_detections = [d for d in detections if d.get('page_num', 0) == page_num]
                
                if page_detections:
                    logger.info(f"Found {len(page_detections)} detections for page {page_num + 1}")
                    
                    # Apply redactions to this page
                    redacted_page_count = self._redact_page(page, page_detections, new_doc)
                    redaction_count += redacted_page_count
                    
                    logger.info(f"Page {page_num + 1}: Applied {redacted_page_count} redactions")
                else:
                    # No redactions needed for this page, copy original
                    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.show_pdf_page(page.rect, doc, page_num)
                    logger.info(f"Page {page_num + 1}: No redactions needed, copied original")
            
            # Save the new multi-page PDF
            new_doc.save(output_path)
            new_doc.close()
            
            logger.info(f"Applied {redaction_count} total redactions across {len(doc)} pages")
            logger.info(f"Saved multi-page redacted PDF to: {output_path}")
            
            return {
                "success": True,
                "total_redactions": redaction_count,
                "pages_processed": len(doc),
                "output_path": output_path
            }
            
        except Exception as e:
            logger.error(f"Redaction failed: {e}")
            new_doc.close()
            return {"success": False, "error": str(e)}
    
    def _redact_page(self, page, page_detections: List[Dict], new_doc) -> int:
        """
        Apply redactions to a single page
        
        Args:
            page: PyMuPDF page object
            page_detections: Detections for this page
            new_doc: New document to add redacted page to
            
        Returns:
            Number of redactions applied
        """
        # Convert page to high-resolution image
        mat = fitz.Matrix(self.scale_factor, self.scale_factor)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Apply redactions to this page
        draw = ImageDraw.Draw(img)
        redaction_count = 0
        
        for detection in page_detections:
            coords = detection.get('coordinates', [])
            if coords and len(coords) >= 4:
                redaction_count += self._apply_single_redaction(img, draw, detection, coords)
        
        # Convert redacted image back to PDF page
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        
        # Create new page from redacted image
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_bytes.getvalue())
        
        return redaction_count
    
    def _apply_single_redaction(self, img: Image.Image, draw: ImageDraw.Draw, detection: Dict, coords: List[float]) -> int:
        """
        Apply a single redaction to an image
        
        Args:
            img: PIL Image object
            draw: ImageDraw object
            detection: Detection dictionary
            coords: Coordinates for redaction
            
        Returns:
            1 if redaction applied, 0 if failed
        """
        try:
            # Scale coordinates for the high-resolution image
            x1, y1, x2, y2 = coords[:4]
            x1, y1, x2, y2 = int(x1 * self.scale_factor), int(y1 * self.scale_factor), int(x2 * self.scale_factor), int(y2 * self.scale_factor)
            
            detection_type = detection.get('category', detection.get('type', 'unknown'))
            detection_text = detection.get('text', detection.get('match_text', 'content'))
            
            logger.debug(f"Applying redaction: {detection_type} = '{detection_text}' at [{x1}, {y1}, {x2}, {y2}]")
            
            if 'image' in detection_type or 'photo' in detection_type or 'signature' in detection_type:
                # Blur images
                try:
                    region = img.crop((x1, y1, x2, y2))
                    blurred = region.filter(ImageFilter.GaussianBlur(radius=10))
                    img.paste(blurred, (x1, y1))
                    logger.debug(f"BLURRED {detection_type}: '{detection_text}'")
                except Exception as e:
                    logger.warning(f"Blur failed, using blackout: {e}")
                    draw.rectangle([x1, y1, x2, y2], fill='black')
                    logger.debug(f"BLACKED OUT {detection_type}: '{detection_text}'")
            else:
                # Black out text
                draw.rectangle([x1, y1, x2, y2], fill='black')
                logger.debug(f"BLACKED OUT {detection_type}: '{detection_text}'")
            
            return 1
            
        except Exception as e:
            logger.error(f"Failed to apply redaction: {e}")
            return 0
    
    def apply_single_page_redaction(self, page, detections: List[Dict], output_path: str):
        """
        Apply redaction to a single page document (legacy method for compatibility)
        
        Args:
            page: PyMuPDF page object
            detections: List of detection dictionaries
            output_path: Path to save redacted document
        """
        logger.info("Starting single page redaction process")
        
        if not detections:
            logger.warning("No detections to redact")
            return
        
        # Convert to image
        logger.info("Converting PDF page to high-resolution image")
        mat = fitz.Matrix(self.scale_factor, self.scale_factor)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        draw = ImageDraw.Draw(img)
        
        logger.info(f"Image size: {img.width}x{img.height}")
        
        redaction_count = 0
        
        for idx, detection in enumerate(detections):
            logger.info(f"Processing redaction {idx + 1}/{len(detections)}")
            
            text = detection['text']
            category = detection['category']
            coordinates = detection['coordinates']
            
            logger.debug(f"Target: {category} = '{text}'")
            logger.debug(f"Original coordinates: {coordinates}")
            
            # Scale coordinates
            x0, y0, x1, y1 = coordinates
            scaled_coords = [
                max(0, int(x0 * self.scale_factor)),
                max(0, int(y0 * self.scale_factor)),
                min(img.width, int(x1 * self.scale_factor)),
                min(img.height, int(y1 * self.scale_factor))
            ]
            
            logger.debug(f"Scaled coordinates: {scaled_coords}")
            
            # Apply redaction based on category
            if category.startswith('image_'):
                logger.debug("Applying image redaction")
                try:
                    if category == 'image_photo' or category == 'image_signature':
                        # Blur for photos and signatures
                        region = img.crop(scaled_coords)
                        blurred = region.filter(ImageFilter.GaussianBlur(radius=12))
                        img.paste(blurred, scaled_coords)
                        logger.info(f"BLURRED {category}: '{text}'")
                    else:
                        # Black out for other images
                        draw.rectangle(scaled_coords, fill=(0, 0, 0))
                        logger.info(f"BLACKED OUT {category}: '{text}'")
                except Exception as e:
                    logger.error(f"Image redaction failed: {e}")
                    # Fallback to black rectangle
                    draw.rectangle(scaled_coords, fill=(0, 0, 0))
                    logger.info(f"FALLBACK BLACKOUT: '{text}'")
            else:
                # Text redaction - always black out
                logger.debug("Applying text redaction")
                draw.rectangle(scaled_coords, fill=(0, 0, 0))
                logger.info(f"BLACKED OUT {category}: '{text}'")
            
            redaction_count += 1
            time.sleep(0.05)
        
        # Save result
        logger.info("Saving redacted document")
        
        # Convert PIL image back to PDF using PyMuPDF
        temp_img_path = output_path.replace('.pdf', '_temp.png')
        img.save(temp_img_path, format='PNG', quality=95)
        
        # Create new PDF with the redacted image
        new_doc = fitz.open()
        page_width = 595  # A4 width in points
        page_height = 842  # A4 height in points
        new_page = new_doc.new_page(width=page_width, height=page_height)
        
        # Insert the redacted image
        img_rect = fitz.Rect(0, 0, page_width, page_height)
        new_page.insert_image(img_rect, filename=temp_img_path)
        
        # Save the PDF
        new_doc.save(output_path)
        new_doc.close()
        
        # Clean up temp image
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        
        logger.info(f"Applied {redaction_count} total redactions")
        logger.info(f"Saved to: {output_path}")