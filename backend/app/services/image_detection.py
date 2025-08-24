"""
Image Detection Service for detecting images in PDF documents
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ImageDetectionService:
    """Service for detecting images in PDF documents"""
    
    def __init__(self):
        self.setup_image_classification()
        logger.info("Image Detection Service initialized")
    
    def setup_image_classification(self):
        """Setup image classification rules"""
        self.image_classification_rules = {
            'photo': {
                'min_width': 30, 'max_width': 150,
                'min_height': 30, 'max_height': 150,
                'min_aspect': 0.6, 'max_aspect': 1.7,
                'description': 'Personal photo/passport image'
            },
            'signature': {
                'min_width': 40, 'max_width': 250,
                'min_height': 15, 'max_height': 80,
                'min_aspect': 1.5, 'max_aspect': 8.0,
                'description': 'Signature or handwritten text'
            },
            'logo': {
                'min_width': 15, 'max_width': 100,
                'min_height': 15, 'max_height': 100,
                'min_aspect': 0.3, 'max_aspect': 3.0,
                'description': 'Logo or institutional mark'
            }
        }
        logger.debug("Image classification rules configured")
    
    def detect_images(self, page) -> List[Dict]:
        """
        Detect images in a PDF page with comprehensive analysis
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of image detection dictionaries
        """
        logger.info("Starting detailed image detection")
        
        # Method 1: Direct image extraction
        images = page.get_images()
        logger.info(f"Direct extraction: Found {len(images)} images")
        
        image_detections = []
        
        for img_index, img_info in enumerate(images):
            logger.info(f"Processing image {img_index + 1}/{len(images)}")
            
            try:
                xref = img_info[0]
                logger.debug(f"Image XREF: {xref}")
                
                img_rects = page.get_image_rects(xref)
                logger.debug(f"Found {len(img_rects)} rectangles for this image")
                
                for rect_idx, rect in enumerate(img_rects):
                    logger.debug(f"Analyzing rectangle {rect_idx + 1}")
                    
                    x0, y0, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
                    width = x1 - x0
                    height = y1 - y0
                    area = width * height
                    aspect_ratio = width / height if height > 0 else 1
                    
                    logger.debug(f"Dimensions: {width:.1f}x{height:.1f} (area: {area:.1f}, aspect: {aspect_ratio:.2f})")
                    
                    # Classify image type
                    img_type = self.classify_image(width, height, aspect_ratio, img_index)
                    
                    if img_type:
                        coordinates = [x0, y0, x1, y1]
                        
                        detection = {
                            'text': f'IMAGE_{img_index}_{img_type}',
                            'category': f'image_{img_type}',
                            'coordinates': coordinates,
                            'confidence': 0.8,
                            'method': 'IMAGE_ANALYSIS',
                            'image_type': img_type,
                            'dimensions': f"{width:.1f}x{height:.1f}"
                        }
                        
                        image_detections.append(detection)
                        
                        logger.info(f"VALID {img_type.upper()}: {width:.1f}x{height:.1f} at {coordinates}")
                    else:
                        logger.debug("Not classified as PII image")
                    
            except Exception as e:
                logger.error(f"Error processing image {img_index}: {e}")
        
        logger.info(f"Image detection complete: {len(image_detections)} PII images found")
        return image_detections
    
    def classify_image(self, width: float, height: float, aspect_ratio: float, img_index: int) -> Optional[str]:
        """
        Classify image with detailed analysis
        
        Args:
            width: Image width
            height: Image height
            aspect_ratio: Width/height ratio
            img_index: Image index for logging
            
        Returns:
            Image type string or None
        """
        logger.debug(f"Classifying image {img_index}: {width:.1f}x{height:.1f} (aspect: {aspect_ratio:.2f})")
        
        for img_type, rules in self.image_classification_rules.items():
            logger.debug(f"Testing {img_type} rules")
            
            width_ok = rules['min_width'] <= width <= rules['max_width']
            height_ok = rules['min_height'] <= height <= rules['max_height']
            aspect_ok = rules['min_aspect'] <= aspect_ratio <= rules['max_aspect']
            
            if width_ok and height_ok and aspect_ok:
                logger.info(f"CLASSIFIED as {img_type}: {rules['description']}")
                return img_type
        
        logger.debug("No classification match")
        return None
