"""
Main PII Processor Service that orchestrates all other services
"""

import time
import fitz
import logging
from typing import List, Dict, Any, Tuple

from .ocr_service import OCRService
from .pii_detection import PIIDetectionService
from .llm_agent import LLMAgentService
from .coordinate_mapper import CoordinateMapperService
from .redaction_engine import RedactionEngineService
from .image_detection import ImageDetectionService
from .job_manager import JobManagerService
from .prompt_interpreter import PromptInterpreterService
from ..models.job import ProcessingStats

logger = logging.getLogger(__name__)

class PIIProcessorService:
    """Main service that orchestrates PII detection and redaction"""
    
    def __init__(self):
        # Initialize all services
        self.ocr_service = OCRService()
        self.pii_detection = PIIDetectionService()
        self.llm_agent = LLMAgentService()
        self.coordinate_mapper = CoordinateMapperService()
        self.redaction_engine = RedactionEngineService()
        self.image_detection = ImageDetectionService()
        self.job_manager = JobManagerService()
        self.prompt_interpreter = PromptInterpreterService(self.llm_agent)
        
        # Processing stats
        self.stats = ProcessingStats()
        self.current_job_id = None
        
        logger.info("PII Processor Service initialized with all sub-services")
    
    def process_document(self, pdf_path: str, output_path: str, job_id: str = None, redaction_prompt: str = "hide all personal information") -> Dict[str, Any]:
        """
        Process document with ultra-detailed logging and comprehensive PII detection
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output PDF
            job_id: Optional job ID for progress tracking
            
        Returns:
            Processing results dictionary
        """
        self.current_job_id = job_id
        self.stats = ProcessingStats()  # Reset stats
        
        logger.info("STARTING PROMPT-BASED PII PROCESSING 🚀")
        logger.info(f"Input file: {pdf_path}")
        logger.info(f"Output file: {output_path}")
        logger.info(f"Redaction prompt: '{redaction_prompt}'")
        
        # Parse user's redaction preferences
        redaction_rules = self.prompt_interpreter.parse_redaction_prompt(redaction_prompt)
        logger.info(f"Parsed redaction rules: {redaction_rules}")
        
        start_time = time.time()
        
        try:
            # Update job progress
            self._update_job_progress(10, "Loading PDF document")
            
            # Load document
            logger.info("Loading PDF document")
            doc = fitz.open(pdf_path)
            logger.info(f"PDF opened successfully: {len(doc)} pages")
            
            all_detections = []
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                # Update job progress
                page_progress = 20 + (page_num / len(doc)) * 60  # 20-80% for page processing
                self._update_job_progress(int(page_progress), f"Processing page {page_num + 1}/{len(doc)}")
                
                # Extract text from this page
                words, full_text, extraction_stats = self._extract_text_comprehensive(page)
                
                # Detect PII on this page
                text_detections = self._detect_pii_with_rules(full_text, words, redaction_rules)
                
                # Detect images on this page
                image_detections = self.image_detection.detect_images(page)
                
                # Add page number and coordinates to detections
                page_detections = []
                for detection in text_detections + image_detections:
                    detection['page_num'] = page_num
                    
                    # Find coordinates if not already present
                    if 'coordinates' not in detection and detection.get('text'):
                        coords = self.coordinate_mapper.find_coordinates(
                            detection['text'], words, detection.get('category', 'unknown')
                        )
                        if coords:
                            # Validate coordinates
                            is_valid, reason = self.coordinate_mapper.validate_coordinates(coords, detection['text'])
                            if is_valid:
                                detection['coordinates'] = coords
                                page_detections.append(detection)
                                logger.info(f"Added detection: {detection['category']} = '{detection['text']}'")
                            else:
                                logger.warning(f"Invalid coordinates for '{detection['text']}': {reason}")
                        else:
                            logger.warning(f"No coordinates found for '{detection['text']}'")
                    elif 'coordinates' in detection:
                        page_detections.append(detection)
                
                all_detections.extend(page_detections)
                logger.info(f"Page {page_num + 1}: {len(page_detections)} valid detections")
            
            logger.info(f"Total detections across all pages: {len(all_detections)}")
            
            # Update job progress
            self._update_job_progress(85, "Applying redactions")
            
            # Apply redaction to create a new multi-page PDF
            logger.info("Applying redaction to all pages")
            redaction_result = self.redaction_engine.apply_redactions(doc, all_detections, output_path)
            
            doc.close()
            
            processing_time = time.time() - start_time
            
            # Final results
            results = {
                'success': True,
                'total_detections': len(all_detections),
                'text_detections': len([d for d in all_detections if not d.get('category', '').startswith('image_')]),
                'image_detections': len([d for d in all_detections if d.get('category', '').startswith('image_')]),
                'processing_time': processing_time,
                'stats': self.stats.__dict__,
                'output_file': output_path,
                'redaction_result': redaction_result
            }
            
            # Update job completion
            self._update_job_progress(100, "Processing completed successfully")
            if self.current_job_id:
                self.job_manager.mark_job_completed(self.current_job_id, results)
            
            logger.info("COMPREHENSIVE PROCESSING SUMMARY")
            logger.info(f"Total processing time: {processing_time:.2f} seconds")
            logger.info(f"Total detections: {len(all_detections)}")
            
            return results
            
        except Exception as e:
            logger.error(f"CRITICAL ERROR: {e}")
            if self.current_job_id:
                self.job_manager.mark_job_failed(self.current_job_id, str(e))
            return {'success': False, 'error': str(e)}
    
    def _extract_text_comprehensive(self, page) -> Tuple[List, str, Dict]:
        """Extract text with multiple methods and comprehensive logging"""
        logger.debug("Starting comprehensive text extraction")
        
        extraction_results = {}
        
        # Method 1: Word-level extraction
        logger.debug("Method 1: Word-level extraction")
        words = page.get_text("words")
        extraction_results['words'] = len(words)
        self.stats.raw_text_extractions += 1
        logger.debug(f"Extracted {len(words)} words")
        
        # Method 2: Full text extraction
        logger.debug("Method 2: Full text extraction")
        full_text = page.get_text()
        extraction_results['characters'] = len(full_text)
        logger.debug(f"Extracted {len(full_text)} characters")
        
        # Method 3: Dictionary extraction for context
        logger.debug("Method 3: Dictionary extraction")
        text_dict = page.get_text("dict")
        extraction_results['blocks'] = len(text_dict.get('blocks', []))
        logger.debug(f"Extracted {extraction_results['blocks']} text blocks")
        
        # Method 4: OCR for scanned documents
        if len(words) == 0 and len(full_text) == 0:
            logger.info("Method 4: OCR for scanned document")
            words, full_text = self.ocr_service.extract_text_from_page(page)
            extraction_results['words'] = len(words)
            extraction_results['characters'] = len(full_text)
            extraction_results['ocr_used'] = True
            logger.info(f"OCR extracted {len(words)} words, {len(full_text)} characters")
        else:
            extraction_results['ocr_used'] = False
        
        # Log sample text for debugging
        sample_text = full_text[:200].replace('\n', ' ').strip()
        logger.debug(f"Sample text: '{sample_text}...'")
        
        logger.debug("Text extraction complete")
        return words, full_text, extraction_results
    
    def _detect_pii_comprehensive(self, text: str, words: List) -> List[Dict]:
        """Comprehensive PII detection with AI validation"""
        logger.info("Starting comprehensive PII detection")
        
        # Get initial detections
        detections = self.pii_detection.detect_pii(text, words)
        
        # Validate each detection with intelligent pattern + LLM analysis
        validated_detections = []
        for detection in detections:
            match_text = detection['text']
            category = detection['category']
            
            # Step 1: Pattern-based validation (fallback for obvious cases)
            is_obvious_pii = self._is_obvious_personal_info(match_text, category)
            
            if is_obvious_pii:
                # Skip LLM for obvious personal information
                validated_detections.append(detection)
                self.stats.successful_detections += 1
                logger.info(f"OBVIOUS PII DETECTED: {category} = '{match_text}' (pattern-based)")
                continue
            
            # Step 2: LLM analysis for ambiguous cases
            should_redact = not self.llm_agent.analyze_with_agent(match_text, text, category)
            
            if should_redact:
                validated_detections.append(detection)
                self.stats.successful_detections += 1
                logger.info(f"VALID PII DETECTED: {category} = '{match_text}' (LLM-validated)")
            else:
                logger.warning(f"GROQ AGENT BLOCKED: '{match_text}' (determined as non-PII by AI)")
                self.stats.rejected_detections += 1
        
        logger.info(f"PII detection summary: {len(validated_detections)} validated detections")
        return validated_detections
    
    def _detect_pii_with_rules(self, text: str, words: List, redaction_rules) -> List[Dict]:
        """PII detection with prompt-based filtering"""
        logger.info("Starting prompt-based PII detection")
        
        # Get initial detections from all patterns
        detections = self.pii_detection.detect_pii(text, words)
        logger.info(f"Initial pattern detections: {len(detections)}")
        
        # Filter detections based on user's redaction rules
        filtered_detections = []
        for detection in detections:
            should_redact = self.prompt_interpreter.should_redact_detection(detection, redaction_rules)
            
            if should_redact:
                filtered_detections.append(detection)
                self.stats.successful_detections += 1
                logger.info(f"PROMPT-BASED DETECTION: {detection['category']} = '{detection['text']}'")
            else:
                self.stats.rejected_detections += 1
                logger.debug(f"PROMPT-FILTERED OUT: {detection['category']} = '{detection['text']}'")
        
        logger.info(f"Prompt-based filtering: {len(filtered_detections)} detections match user preferences")
        return filtered_detections
    
    def _is_obvious_personal_info(self, text: str, category: str) -> bool:
        """
        Pattern-based detection for obvious personal information
        Catches clear cases that LLM might miss due to context confusion
        """
        text_lower = text.lower().strip()
        
        # Skip very short or obviously non-personal text
        if len(text_lower) <= 2:
            return False
        
        # Common non-personal words to skip
        non_personal_words = {
            'based', 'rank', 'option', 'details', 'name', 'student', 'candidate', 
            'date', 'address', 'phone', 'email', 'number', 'code', 'id', 'roll',
            'application', 'registration', 'allotment', 'admission', 'fee', 'total',
            'amount', 'page', 'no', 'view', 'system', 'generated', 'letters'
        }
        
        if text_lower in non_personal_words:
            return False
        
        if category == 'person_names':
            # Obvious name patterns
            if (len(text) >= 3 and 
                text[0].isupper() and 
                text.isalpha() and 
                text_lower not in non_personal_words and
                not any(word in text_lower for word in ['details', 'rank', 'option', 'based'])):
                return True
                
        elif category == 'identification_numbers':
            # Long numeric strings are usually IDs
            if text.isdigit() and len(text) >= 8:
                return True
            # Mixed alphanumeric IDs
            if len(text) >= 6 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
                return True
                
        elif category == 'phone_numbers':
            # Clear phone number patterns
            digit_count = sum(1 for c in text if c.isdigit())
            if digit_count >= 10:
                return True
                
        elif category == 'email_addresses':
            # Clear email patterns
            if '@' in text and '.' in text:
                return True
        
        return False
    
    def _update_job_progress(self, progress: int, message: str):
        """Update job progress if job ID is set"""
        if self.current_job_id:
            self.job_manager.update_job_progress(self.current_job_id, progress, message)
            self.job_manager.add_job_log(self.current_job_id, f"[{progress}%] {message}")
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get job status"""
        return self.job_manager.get_job_status_dict(job_id)
    
    def create_processing_job(self, filename: str, input_path: str, output_path: str):
        """Create a new processing job"""
        return self.job_manager.create_job(filename, input_path, output_path)
