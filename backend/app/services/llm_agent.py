"""
LLM Agent Service using GROQ API for intelligent PII validation
"""

import requests
import logging
from typing import Tuple, Optional

from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMAgentService:
    """LLM service for intelligent PII validation using GROQ"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_BASE_URL
        self.model = settings.GROQ_MODEL
        self.timeout = settings.GROQ_TIMEOUT
        logger.info("LLM Agent Service initialized")
    
    def analyze_with_agent(self, text: str, full_context: str, category: str) -> bool:
        """
        Intelligently determine if text should NOT be redacted using adaptive GROQ analysis
        
        Args:
            text: Text to analyze
            full_context: Surrounding context
            category: PII category
            
        Returns:
            True if text should be preserved (not redacted)
        """
        try:
            # Generate context-aware prompt based on category
            prompt = self._generate_adaptive_prompt(text, full_context, category)
            
            response = self.call_groq_api(prompt, max_tokens=10)
            
            # Intelligent response parsing
            decision = self._parse_agent_response(response, text, category)
            
            if decision:
                logger.info(f"GROQ DECISION: '{text}' → NON-PII (category: {category}) - should NOT be redacted")
                return True
            else:
                logger.info(f"GROQ DECISION: '{text}' → PII (category: {category}) - should be redacted")
                return False
                
        except Exception as e:
            logger.warning(f"GROQ agent failed: {e}")
            return False
    
    def _generate_adaptive_prompt(self, text: str, full_context: str, category: str) -> str:
        """
        CAPG (Context-Aware Prompt Generation) Algorithm
        
        Research Algorithm for dynamic LLM prompt optimization:
        - Category-Specific Template Selection
        - Context Window Optimization
        - Decision Boundary Clarification
        """
        context_window = self.extract_surrounding_context(text, full_context, 120)
        
        base_prompt = f'TEXT: "{text}"\nCONTEXT: "{context_window}"\n\n'
        
        if category == 'person_names':
            return base_prompt + f"""Look at "{text}" - is this a PERSON'S NAME?

REDACT (answer YES) if it's ANY of these:
- Human names: ASHISH, ARUN, KUMAR, SANGEETA, URVASHI, etc.
- Names in any format: FirstName, LASTNAME, Full Name
- Father/Mother names in forms
- Student/Candidate actual names
- Any word that could be someone's real name

KEEP (answer NO) only if it's clearly:
- Labels: "Name:", "Student:", "Candidate:" 
- Generic words: "Based", "Rank", "Option", "Details"
- System terms: "Registration", "Application"

Examples:
- "ASHISH" → YES (person's name)
- "Name:" → NO (just a label)
- "Based" → NO (generic word)

Answer: YES or NO"""

        elif category == 'identification_numbers':
            return base_prompt + f"""Look at "{text}" - is this a PERSONAL ID that should be HIDDEN?

REDACT (answer YES) if it's:
- Application numbers: 128230000295, etc.
- Roll numbers, Student IDs, Registration numbers
- Aadhar numbers, PAN card numbers
- Any long number (6+ digits) that identifies a person
- Account numbers, Reference numbers
- Phone numbers, mobile numbers

KEEP (answer NO) only if it's:
- Small numbers: 1, 2, 3, 10, 464
- Years: 2023, 2024, 2025
- Percentages or scores
- Version numbers

Examples:
- "128230000295" → YES (long ID number)
- "2023" → NO (just a year)
- "464" → NO (small number)

Answer: YES or NO"""

        elif category == 'phone_numbers':
            return base_prompt + f"""Look at "{text}" - is this a PHONE NUMBER that should be HIDDEN?

REDACT (answer YES) if it's:
- Phone numbers: +91-9876543210, 9876543210, etc.
- Mobile numbers with 10+ digits
- Contact numbers
- Any number that looks like a phone

KEEP (answer NO) if it's:
- Short codes: 123, 456
- Years: 2023, 2024
- Technical numbers

Answer: YES or NO"""

        else:
            # Generic prompt for other categories - default to redacting personal info
            return base_prompt + f"""Look at "{text}" - should this PERSONAL INFO be HIDDEN?

REDACT (answer YES) if it's:
- Addresses: "Delhi", "Mumbai", specific locations
- Dates: birth dates, important personal dates
- Personal details, private information
- Anything that identifies a specific person

KEEP (answer NO) only if it's clearly:
- Generic labels: "Date:", "Address:"
- System terms: "Registration", "Details"
- Common words with no personal meaning

When in doubt, REDACT to protect privacy.

Answer: YES or NO"""
    
    def _parse_agent_response(self, response: str, text: str, category: str) -> bool:
        """
        IRPS (Intelligent Response Parsing System) Algorithm
        
        Research Algorithm for LLM response interpretation:
        - Primary Decision Logic
        - Fallback Heuristic Analysis
        - Category-Specific Safety Defaults
        """
        if not response:
            return False
        
        response_upper = response.upper().strip()
        
        # Primary decision logic - bias toward redacting personal info
        if 'YES' in response_upper:
            return True
        elif 'NO' in response_upper:
            # For person names and ID numbers, be extra cautious
            if category in ['person_names', 'identification_numbers']:
                # Only skip redaction if very confident it's not personal
                if any(term in response_upper for term in ['TECHNICAL', 'SYSTEM', 'LABEL', 'GENERIC']):
                    return False
                else:
                    # When in doubt with names/IDs, redact them
                    logger.warning(f"GROQ said NO but redacting {category} '{text}' for safety")
                    return True
            return False
        
        # Fallback heuristics for unclear responses
        logger.warning(f"Unclear GROQ response: '{response}' for '{text}' - applying fallback logic")
        
        # Category-specific fallback logic - default to redacting
        if category == 'person_names':
            # Only preserve if clearly technical
            tech_indicators = ['js', 'py', 'api', 'sql', 'git', 'dev', 'sys', 'app', 'web']
            if any(indicator in text.lower() for indicator in tech_indicators):
                logger.info(f"Fallback: '{text}' appears technical - preserving")
                return False
            else:
                # Default to redacting names when unclear
                logger.info(f"Fallback: '{text}' might be personal name - redacting for safety")
                return True
        
        elif category == 'identification_numbers':
            # Only preserve very short numbers or obvious technical codes
            if len(text) <= 3:
                logger.info(f"Fallback: '{text}' is very short - might be technical")
                return False
            else:
                # Default to redacting ID numbers when unclear
                logger.info(f"Fallback: '{text}' might be personal ID - redacting for safety")
                return True
        
        # Default to redacting for safety
        logger.info(f"Fallback: No clear category match - redacting '{text}' for safety")
        return True
    
    def validate_with_agent(self, text: str, category: str, context: str = "") -> Tuple[Optional[bool], str]:
        """
        Use GROQ LLM to validate if text is actual PII vs form label
        
        Args:
            text: Text to validate
            category: PII category
            context: Additional context
            
        Returns:
            Tuple of (is_valid_or_none, reason)
        """
        try:
            prompt = f"""You are a smart PII detection agent. Analyze if the following text is actual USER DATA (PII) or just a FORM LABEL.

Text: "{text}"
Category: {category}

RULES:
- USER DATA (YES): Personal info like "URVASHI", "john.doe@email.com", "8448252782"
- FORM LABEL (NO): Template words like "Name:", "Email:", "Phone:", "Registration:"

Answer: YES (if actual PII) or NO (if form label)"""

            response = self.call_groq_api(prompt, max_tokens=50)
            
            if response and 'YES' in response.upper():
                return True, "GROQ: Valid PII"
            else:
                return False, "GROQ: Form label"
                
        except Exception as e:
            return None, f"GROQ error: {e}"
    
    def call_groq_api(self, prompt: str, max_tokens: int = 10) -> str:
        """
        Helper method to call GROQ API with error handling
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            API response content
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return content.strip()
            else:
                logger.warning(f"GROQ API error: {response.status_code} - {response.text[:100]}")
                return ""
                
        except Exception as e:
            logger.warning(f"GROQ API call failed: {e}")
            return ""
    
    def extract_surrounding_context(self, target_text: str, full_text: str, window_size: int = 100) -> str:
        """
        Extract surrounding context around target text for better analysis
        
        Args:
            target_text: Text to find context for
            full_text: Full document text
            window_size: Size of context window
            
        Returns:
            Context string
        """
        try:
            target_pos = full_text.lower().find(target_text.lower())
            if target_pos == -1:
                return full_text[:window_size]
            
            start_pos = max(0, target_pos - window_size)
            end_pos = min(len(full_text), target_pos + len(target_text) + window_size)
            
            context = full_text[start_pos:end_pos].strip()
            return context
            
        except Exception as e:
            logger.warning(f"Context extraction failed: {e}")
            return full_text[:window_size]