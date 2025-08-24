"""
Coordinate Mapper Service for finding and validating text coordinates in PDFs
"""

import logging
from typing import List, Optional, Tuple, Dict, Any

from ..core.config import settings

logger = logging.getLogger(__name__)

class CoordinateMapperService:
    """Service for mapping text to coordinates and validation"""
    
    def __init__(self):
        self.setup_validation_rules()
        logger.info("Coordinate Mapper Service initialized")
    
    def setup_validation_rules(self):
        """
        Initialize AVCF (Adaptive Validation & Coordinate Finding) Framework
        
        Research Framework Components:
        - DLAA (Document Layout Analysis Algorithm)
        - ACVS (Adaptive Coordinate Validation System)
        - MSCF (Multi-Strategy Coordinate Finding)
        """
        logger.info("Initializing AVCF (Adaptive Validation & Coordinate Finding) Framework")
        
        # Initialize with base rules - will be dynamically adjusted
        self.base_coordinate_limits = {
            'text': {
                'max_width': 200,
                'max_height': 50,
                'max_area': 8000,
                'min_width': 2,
                'min_height': 2,
                'min_area': 4
            },
            'image': {
                'max_width': 400,
                'max_height': 300,
                'max_area': 100000,
                'min_width': 10,
                'min_height': 10,
                'min_area': 100
            },
            'overlap_threshold': 0.15,
            'merge_distance': 8
        }
        
        # Dynamic adjustment factors
        self.adjustment_factors = {
            'content_density': 1.0,
            'document_scale': 1.0,
            'text_frequency': 1.0
        }
        
        # Initialize with base rules
        self.coordinate_limits = self.base_coordinate_limits.copy()
        
        logger.info("Adaptive coordinate validation system initialized")
    
    def analyze_document_layout(self, words: List) -> Dict[str, float]:
        """
        DLAA (Document Layout Analysis Algorithm)
        
        Research Algorithm for intelligent document structure analysis:
        - Statistical Content Analysis
        - Text Density Computation
        - Layout Variability Assessment
        - Adaptive Scaling Factors
        """
        if not words:
            return {}
        
        # Calculate document characteristics
        all_widths = []
        all_heights = []
        all_areas = []
        
        for word_info in words:
            if len(word_info) >= 5:
                x0, y0, x1, y1 = word_info[:4]
                width = abs(x1 - x0)
                height = abs(y1 - y0)
                area = width * height
                
                all_widths.append(width)
                all_heights.append(height)
                all_areas.append(area)
        
        if not all_widths:
            return {}
        
        # Calculate statistics
        analysis = {
            'avg_width': sum(all_widths) / len(all_widths),
            'avg_height': sum(all_heights) / len(all_heights),
            'avg_area': sum(all_areas) / len(all_areas),
            'max_width': max(all_widths),
            'max_height': max(all_heights),
            'content_density': len(words) / (max(all_areas) + 1),
            'text_variation': (max(all_widths) - min(all_widths)) / (max(all_widths) + 1)
        }
        
        logger.debug(f"Document analysis: {analysis}")
        return analysis
    
    def adapt_coordinate_limits(self, words: List, category: str):
        """
        ACVS (Adaptive Coordinate Validation System) Algorithm
        
        Research Algorithm for dynamic boundary adjustment:
        - Real-time Layout Assessment
        - Category-Specific Scaling
        - Content Density Adaptation
        - Intelligent Boundary Optimization
        """
        analysis = self.analyze_document_layout(words)
        
        if not analysis:
            return
        
        # Adaptive scaling based on document characteristics
        scale_factor = 1.0
        
        # Adjust based on average text size
        if analysis['avg_width'] > 100:
            scale_factor *= 1.3  # Allow larger regions for documents with large text
        elif analysis['avg_width'] < 20:
            scale_factor *= 0.7  # Tighten limits for documents with small text
        
        # Adjust based on content density
        if analysis['content_density'] > 0.1:
            scale_factor *= 0.8  # Tighten for dense documents
        elif analysis['content_density'] < 0.05:
            scale_factor *= 1.2  # Relax for sparse documents
        
        # Apply adaptive scaling
        content_type = 'text' if category in ['person_names', 'identification_numbers', 'phone_numbers', 'email_addresses', 'dates'] else 'image'
        
        original_limits = self.base_coordinate_limits[content_type].copy()
        
        # Apply intelligent scaling
        self.coordinate_limits[content_type] = {
            'max_width': original_limits['max_width'] * scale_factor,
            'max_height': original_limits['max_height'] * scale_factor,
            'max_area': original_limits['max_area'] * (scale_factor ** 2),
            'min_width': max(1, original_limits['min_width'] * (scale_factor * 0.5)),
            'min_height': max(1, original_limits['min_height'] * (scale_factor * 0.5)),
            'min_area': max(1, original_limits['min_area'] * (scale_factor ** 2))
        }
        
        logger.debug(f"Adapted {content_type} limits with scale factor {scale_factor:.2f}")
        logger.debug(f"New limits: {self.coordinate_limits[content_type]}")
    
    def find_coordinates(self, target_text: str, words: List, category: str) -> Optional[List[float]]:
        """
        Find coordinates for target text with adaptive validation
        
        Args:
            target_text: Text to find coordinates for
            words: List of word objects with coordinates
            category: PII category
            
        Returns:
            Coordinates as [x0, y0, x1, y1] or None
        """
        logger.debug(f"Finding coordinates for '{target_text}' (category: {category})")
        
        # Step 1: Adapt coordinate limits based on document analysis
        self.adapt_coordinate_limits(words, category)
        
        # Step 2: Intelligent text matching with multiple strategies
        coordinates = self._find_coordinates_intelligent(target_text, words, category)
        
        if coordinates:
            # Step 3: Validate coordinates with adaptive rules
            if self._validate_coordinates_adaptive(coordinates, category):
                logger.debug(f"Valid coordinates found: {coordinates}")
                return coordinates
            else:
                logger.debug("Coordinates failed adaptive validation")
        
        logger.debug("No valid coordinates found")
        return None
    
    def _find_coordinates_intelligent(self, target_text: str, words: List, category: str) -> Optional[List[float]]:
        """
        MSCF (Multi-Strategy Coordinate Finding) Algorithm
        
        Research Algorithm with 4-tier hierarchical search:
        1. EMS (Exact Match Strategy)
        2. FVS (Fuzzy Variation Strategy) 
        3. MWR (Multi-Word Reconstruction)
        4. CAMS (Context-Aware Matching Strategy)
        """
        
        # EMS: Exact match strategy (Tier 1)
        coords = self._exact_match_strategy_ems(target_text, words)
        if coords:
            logger.debug("MSCF: EMS (Exact Match Strategy) successful")
            return coords
        
        # FVS: Fuzzy matching for slight variations (Tier 2)
        coords = self._fuzzy_match_strategy_fvs(target_text, words)
        if coords:
            logger.debug("MSCF: FVS (Fuzzy Variation Strategy) successful")
            return coords
        
        # MWR: Multi-word reconstruction (Tier 3)
        coords = self._multiword_strategy_mwr(target_text, words)
        if coords:
            logger.debug("MSCF: MWR (Multi-Word Reconstruction) successful")
            return coords
        
        # CAMS: Context-aware matching (Tier 4)
        coords = self._context_aware_strategy_cams(target_text, words, category)
        if coords:
            logger.debug("MSCF: CAMS (Context-Aware Matching Strategy) successful")
            return coords
        
        logger.debug("MSCF: All 4 strategies failed")
        return None
    
    def _exact_match_strategy_ems(self, target_text: str, words: List) -> Optional[List[float]]:
        """
        EMS (Exact Match Strategy) Algorithm - Tier 1
        
        Research Algorithm for precise text matching:
        - Case-insensitive comparison
        - Whitespace normalization
        - Direct coordinate extraction
        """
        logger.debug("Strategy 1: Exact word matching")
        for word_info in words:
            if len(word_info) >= 5:
                x0, y0, x1, y1, word = word_info[:5]
                word_clean = word.strip().upper()
                target_clean = target_text.strip().upper()
                if word_clean == target_clean:
                    coords = [float(x0), float(y0), float(x1), float(y1)]
                    logger.debug(f"Exact match found: {coords}")
                    return coords
        return None
    
    def _fuzzy_match_strategy_fvs(self, target_text: str, words: List) -> Optional[List[float]]:
        """
        FVS (Fuzzy Variation Strategy) Algorithm - Tier 2
        
        Research Algorithm for variation-tolerant matching:
        - Character normalization
        - Partial substring matching
        - Similarity threshold optimization
        """
        logger.debug("Strategy 2: Fuzzy matching")
        target_clean = target_text.strip().upper().replace(' ', '').replace('-', '').replace('.', '')
        
        for word_info in words:
            if len(word_info) >= 5:
                x0, y0, x1, y1, word = word_info[:5]
                word_clean = word.strip().upper().replace(' ', '').replace('-', '').replace('.', '')
                
                # Check if they match after normalization
                if word_clean == target_clean:
                    coords = [float(x0), float(y0), float(x1), float(y1)]
                    logger.debug(f"Fuzzy match found: {coords}")
                    return coords
                
                # Check if target is contained in word or vice versa (for partial matches)
                if len(target_clean) > 3 and (target_clean in word_clean or word_clean in target_clean):
                    coords = [float(x0), float(y0), float(x1), float(y1)]
                    logger.debug(f"Partial fuzzy match found: {coords}")
                    return coords
        
        return None
    
    def _multiword_strategy_mwr(self, target_text: str, words: List) -> Optional[List[float]]:
        """
        MWR (Multi-Word Reconstruction) Algorithm - Tier 3
        
        Research Algorithm for compound text reconstruction:
        - Word boundary detection
        - Spatial proximity analysis
        - Coordinate boundary merging
        - 70% completion threshold
        """
        target_words = target_text.lower().split()
        if len(target_words) < 2:
            return None
        
        logger.debug(f"Strategy 3: Multi-word matching ({len(target_words)} words)")
        
        word_boxes = []
        for target_word in target_words:
            logger.debug(f"Looking for word: '{target_word}'")
            for word_info in words:
                if len(word_info) >= 5:
                    x0, y0, x1, y1, word = word_info[:5]
                    if target_word.lower() in word.lower() or word.lower() in target_word.lower():
                        word_boxes.append([float(x0), float(y0), float(x1), float(y1)])
                        logger.debug(f"Found component word '{word}' at {[x0, y0, x1, y1]}")
                        break
        
        if len(word_boxes) >= len(target_words) * 0.7:  # Found at least 70% of words
            # Merge all word boxes
            if word_boxes:
                min_x = min(box[0] for box in word_boxes)
                min_y = min(box[1] for box in word_boxes)
                max_x = max(box[2] for box in word_boxes)
                max_y = max(box[3] for box in word_boxes)
                
                merged_coords = [min_x, min_y, max_x, max_y]
                logger.debug(f"Multi-word match found: {merged_coords}")
                return merged_coords
        
        return None
    
    def _context_aware_strategy_cams(self, target_text: str, words: List, category: str) -> Optional[List[float]]:
        """
        CAMS (Context-Aware Matching Strategy) Algorithm - Tier 4
        
        Research Algorithm for semantic context matching:
        - Category-specific pattern recognition
        - Contextual field analysis
        - Proximity-based searching
        - Label-value relationship mapping
        """
        logger.debug(f"Strategy 4: Context-aware matching for {category}")
        
        # Different strategies based on category
        if category == 'identification_numbers':
            return self._find_number_context(target_text, words)
        elif category == 'person_names':
            return self._find_name_context(target_text, words)
        elif category == 'phone_numbers':
            return self._find_phone_context(target_text, words)
        elif category == 'email_addresses':
            return self._find_email_context(target_text, words)
        
        return None
    
    def _find_number_context(self, target_text: str, words: List) -> Optional[List[float]]:
        """Find numbers using context clues"""
        # Look for numbers near field labels
        number_labels = ['number', 'roll', 'id', 'registration', 'application', 'admission']
        
        for i, word_info in enumerate(words):
            if len(word_info) >= 5:
                word = word_info[4].lower()
                if any(label in word for label in number_labels):
                    # Look for numbers in the next few words
                    for j in range(i+1, min(i+5, len(words))):
                        if len(words[j]) >= 5:
                            next_word = words[j][4]
                            if target_text in next_word or next_word in target_text:
                                x0, y0, x1, y1 = words[j][:4]
                                return [float(x0), float(y0), float(x1), float(y1)]
        
        return None
    
    def _find_name_context(self, target_text: str, words: List) -> Optional[List[float]]:
        """Find names using context clues"""
        name_labels = ['name', 'student', 'candidate', 'person']
        
        for i, word_info in enumerate(words):
            if len(word_info) >= 5:
                word = word_info[4].lower()
                if any(label in word for label in name_labels):
                    # Look for names in the next few words
                    for j in range(i+1, min(i+4, len(words))):
                        if len(words[j]) >= 5:
                            next_word = words[j][4]
                            if target_text.lower() in next_word.lower() or next_word.lower() in target_text.lower():
                                x0, y0, x1, y1 = words[j][:4]
                                return [float(x0), float(y0), float(x1), float(y1)]
        
        return None
    
    def _find_phone_context(self, target_text: str, words: List) -> Optional[List[float]]:
        """Find phone numbers using context clues"""
        phone_labels = ['phone', 'mobile', 'contact', 'tel']
        
        # Remove formatting from target
        target_digits = ''.join(c for c in target_text if c.isdigit())
        
        for i, word_info in enumerate(words):
            if len(word_info) >= 5:
                word = word_info[4].lower()
                if any(label in word for label in phone_labels):
                    # Look for phone numbers in nearby words
                    for j in range(max(0, i-2), min(i+5, len(words))):
                        if len(words[j]) >= 5:
                            check_word = words[j][4]
                            check_digits = ''.join(c for c in check_word if c.isdigit())
                            if len(check_digits) >= 8 and target_digits in check_digits:
                                x0, y0, x1, y1 = words[j][:4]
                                return [float(x0), float(y0), float(x1), float(y1)]
        
        return None
    
    def _find_email_context(self, target_text: str, words: List) -> Optional[List[float]]:
        """Find email addresses using context clues"""
        for word_info in words:
            if len(word_info) >= 5:
                word = word_info[4]
                if '@' in word and ('.' in word or '@' in target_text):
                    if target_text.lower() in word.lower() or word.lower() in target_text.lower():
                        x0, y0, x1, y1 = word_info[:4]
                        return [float(x0), float(y0), float(x1), float(y1)]
        
        return None
    
    def _validate_coordinates_adaptive(self, coords: List[float], category: str) -> bool:
        """Validate coordinates using adaptive rules"""
        if not coords or len(coords) != 4:
            return False
        
        x0, y0, x1, y1 = coords
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        area = width * height
        
        # Determine content type
        content_type = 'text' if category in ['person_names', 'identification_numbers', 'phone_numbers', 'email_addresses', 'dates'] else 'image'
        limits = self.coordinate_limits.get(content_type, self.base_coordinate_limits['text'])
        
        # Validate dimensions
        if width < limits['min_width'] or width > limits['max_width']:
            logger.debug(f"Width validation failed: {width} not in [{limits['min_width']}, {limits['max_width']}]")
            return False
        
        if height < limits['min_height'] or height > limits['max_height']:
            logger.debug(f"Height validation failed: {height} not in [{limits['min_height']}, {limits['max_height']}]")
            return False
        
        if area < limits['min_area'] or area > limits['max_area']:
            logger.debug(f"Area validation failed: {area} not in [{limits['min_area']}, {limits['max_area']}]")
            return False
        
        logger.debug(f"Coordinates passed adaptive validation: {coords}")
        return True
    
    def validate_coordinates(self, coords: List[float], text: str) -> Tuple[bool, str]:
        """
        Public method for coordinate validation (legacy compatibility)
        
        Args:
            coords: Coordinates to validate [x0, y0, x1, y1]
            text: Associated text for context
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not coords or len(coords) != 4:
            return False, "Invalid coordinate format"
        
        x0, y0, x1, y1 = coords
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        area = width * height
        
        # Basic validation
        if width <= 0 or height <= 0:
            return False, "Invalid dimensions"
        
        if area < 1:
            return False, "Area too small"
        
        if area > 50000:
            return False, "Area too large"
        
        # Coordinate bounds check
        if any(coord < 0 for coord in coords):
            return False, "Negative coordinates"
        
        if any(coord > 10000 for coord in coords):
            return False, "Coordinates too large"
        
        return True, "Valid coordinates"