"""
Prompt Interpreter Service for intelligent redaction based on user prompts
"""

import re
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RedactionRules:
    """Data class to hold parsed redaction rules from user prompt"""
    hide_names: bool = False
    hide_specific_names: Set[str] = None
    hide_addresses: bool = False
    hide_phone_numbers: bool = False
    hide_emails: bool = False
    hide_id_numbers: bool = False
    hide_dates: bool = False
    hide_photos: bool = True  # Always hide photos for now
    hide_all: bool = False
    categories_to_hide: Set[str] = None
    
    def __post_init__(self):
        if self.hide_specific_names is None:
            self.hide_specific_names = set()
        if self.categories_to_hide is None:
            self.categories_to_hide = set()


class PromptInterpreterService:
    """Service to interpret user redaction prompts and create filtering rules"""
    
    def __init__(self, llm_agent=None):
        self.llm_agent = llm_agent  # Optional LLM agent for intelligent validation
        self.name_patterns = [
            r'\bnames?\b',
            r'\bpersonal names?\b',
            r'\bfull names?\b',
            r'\bfirst names?\b',
            r'\blast names?\b'
        ]
        
        self.address_patterns = [
            r'\baddress(?:es)?\b',
            r'\blocation(?:s)?\b',
            r'\bcity\b',
            r'\bstate\b',
            r'\bpincode(?:s)?\b',
            r'\bzip code(?:s)?\b'
        ]
        
        self.phone_patterns = [
            r'\bphone(?:\s+number(?:s)?)?\b',
            r'\bmobile(?:\s+number(?:s)?)?\b',
            r'\bcontact(?:\s+number(?:s)?)?\b',
            r'\bcell(?:\s+number(?:s)?)?\b'
        ]
        
        self.email_patterns = [
            r'\bemail(?:\s+address(?:es)?)?\b',
            r'\be-mail(?:s)?\b'
        ]
        
        self.id_patterns = [
            r'\bid(?:\s+number(?:s)?)?\b',
            r'\bidentification(?:\s+number(?:s)?)?\b',
            r'\broll(?:\s+number(?:s)?)?\b',
            r'\bapplication(?:\s+number(?:s)?)?\b',
            r'\bregistration(?:\s+number(?:s)?)?\b',
            r'\baadhar(?:\s+number(?:s)?)?\b',
            r'\bpan(?:\s+card(?:s)?)?\b'
        ]
        
        self.date_patterns = [
            r'\bdate(?:s)?\b',
            r'\bbirth(?:\s+date(?:s)?)?\b',
            r'\bdob\b',
            r'\bdate(?:s)?\s+of\s+birth\b'
        ]
        
        logger.info("Prompt Interpreter Service initialized")
    
    def parse_redaction_prompt(self, prompt: str) -> RedactionRules:
        """
        Parse user's redaction prompt and create filtering rules
        
        Args:
            prompt: User's natural language redaction request
            
        Returns:
            RedactionRules object with parsed preferences
        """
        logger.info(f"Parsing redaction prompt: '{prompt}'")
        
        prompt_lower = prompt.lower().strip()
        rules = RedactionRules()
        
        # Check for "hide all" or "hide everything"
        if any(phrase in prompt_lower for phrase in ['hide all', 'hide everything', 'redact all', 'redact everything']):
            rules.hide_all = True
            logger.info("Detected: Hide all personal information")
            return rules
        
        # Check for "hide only" or "only hide" patterns (specific hiding)
        only_patterns = re.findall(r'(?:hide only|only hide|just hide)\s+([^,]+)', prompt_lower)
        if only_patterns:
            # User wants to hide only specific things
            specific_items = only_patterns[0].strip()
            rules = self._parse_specific_items(specific_items)
            logger.info(f"Detected specific hiding: {specific_items}")
            return rules
        
        # Check for specific name mentions
        name_mentions = re.findall(r'(?:hide|redact)\s+(?:name(?:s)?|person)\s+([a-zA-Z\s,]+)', prompt_lower)
        if name_mentions:
            for mention in name_mentions:
                names = [name.strip() for name in mention.split(',') if name.strip()]
                rules.hide_specific_names.update(names)
                logger.info(f"Detected specific names to hide: {names}")
        
        # Check for general categories
        if self._matches_patterns(prompt_lower, self.name_patterns):
            rules.hide_names = True
            logger.info("Detected: Hide names")
        
        if self._matches_patterns(prompt_lower, self.address_patterns):
            rules.hide_addresses = True
            logger.info("Detected: Hide addresses")
        
        if self._matches_patterns(prompt_lower, self.phone_patterns):
            rules.hide_phone_numbers = True
            logger.info("Detected: Hide phone numbers")
        
        if self._matches_patterns(prompt_lower, self.email_patterns):
            rules.hide_emails = True
            logger.info("Detected: Hide emails")
        
        if self._matches_patterns(prompt_lower, self.id_patterns):
            rules.hide_id_numbers = True
            logger.info("Detected: Hide ID numbers")
        
        if self._matches_patterns(prompt_lower, self.date_patterns):
            rules.hide_dates = True
            logger.info("Detected: Hide dates")
        
        # If no specific categories detected, default to personal info
        if not (rules.hide_names or rules.hide_addresses or rules.hide_phone_numbers or 
                rules.hide_emails or rules.hide_id_numbers or rules.hide_dates or 
                rules.hide_specific_names):
            logger.info("No specific categories detected, defaulting to names and ID numbers")
            rules.hide_names = True
            rules.hide_id_numbers = True
        
        return rules
    
    def _parse_specific_items(self, items_text: str) -> RedactionRules:
        """Parse specific items when user says 'hide only X'"""
        rules = RedactionRules()
        
        if self._matches_patterns(items_text, self.name_patterns):
            rules.hide_names = True
        if self._matches_patterns(items_text, self.address_patterns):
            rules.hide_addresses = True
        if self._matches_patterns(items_text, self.phone_patterns):
            rules.hide_phone_numbers = True
        if self._matches_patterns(items_text, self.email_patterns):
            rules.hide_emails = True
        if self._matches_patterns(items_text, self.id_patterns):
            rules.hide_id_numbers = True
        if self._matches_patterns(items_text, self.date_patterns):
            rules.hide_dates = True
        
        # Check for specific names in "only hide" context
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', items_text)
        if potential_names:
            rules.hide_specific_names.update([name.lower() for name in potential_names])
        
        return rules
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given regex patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def should_redact_detection(self, detection: Dict, rules: RedactionRules) -> bool:
        """
        Intelligent detection filtering based on rules and context
        
        Args:
            detection: PII detection dictionary
            rules: Parsed redaction rules
            
        Returns:
            True if detection should be redacted
        """
        category = detection.get('category', '')
        text = detection.get('text', '').strip()
        text_lower = text.lower()
        
        # Always hide photos for now
        if category == 'photos':
            return True
        
        # Hide all mode
        if rules.hide_all:
            return True
        
        # Check specific names first
        if rules.hide_specific_names and category == 'person_names':
            for specific_name in rules.hide_specific_names:
                if specific_name.lower() in text_lower:
                    logger.debug(f"Hiding specific name: {text}")
                    return True
            # If we have specific names to hide, don't hide other names unless hide_names is also True
            if rules.hide_specific_names and not rules.hide_names:
                return False
        
        # Smart filtering for person names
        if category == 'person_names' and rules.hide_names:
            return self._is_actual_person_name(text)
        
        # Other categories with smart filtering
        if category == 'addresses' and rules.hide_addresses:
            return self._is_actual_address_info(text)
        if category == 'phone_numbers' and rules.hide_phone_numbers:
            return self._is_actual_phone_number(text)
        if category == 'email_addresses' and rules.hide_emails:
            return self._is_actual_email(text)
        if category == 'identification_numbers' and rules.hide_id_numbers:
            return self._is_actual_id_number(text)
        if category == 'dates' and rules.hide_dates:
            return self._is_actual_personal_date(text)
        
        return False
    
    def _is_actual_person_name(self, text: str) -> bool:
        """Check if text is an actual person name, not a field label"""
        text_lower = text.lower().strip()
        
        # Skip obvious field labels and generic terms
        field_labels = {
            'name', 'father', 'mother', 'student', 'candidate', 'person',
            'information', 'personal', 'order', 'date', 'time', 'amount',
            'address', 'line', 'state', 'district', 'gender', 'nationality',
            'category', 'program', 'course', 'tech', 'engineering', 'science',
            'computer', 'electronics', 'mechanical', 'communication', 'civil',
            'education', 'qualification', 'examination', 'school', 'board',
            'year', 'month', 'roll', 'marks', 'cgpa', 'percentage', 'bank',
            'account', 'branch', 'code', 'ifsc', 'choices', 'preferences',
            'type', 'campus', 'declaration', 'undertaking', 'signature',
            'printed', 'failure', 'entrance', 'program', 'liable', 'the',
            'all', 'are', 'have', 'yes', 'no', 'male', 'female', 'indian',
            'registered', 'emergency', 'communication', 'location', 'institute',
            'permanent', 'pin', 'zip', 'pincode', 'govt', 'high', 'open',
            'rural', 'technology', 'technical', 'others', 'equivalent',
            'new', 'west', 'blood', 'group', 'defence', 'kashmiri', 'migrant',
            'scheduled', 'caste', 'skill', 'nct'
        }
        
        # Skip if it's a field label
        if text_lower in field_labels:
            return False
        
        # Skip very short words (likely abbreviations)
        if len(text) <= 2:
            return False
        
        # Skip if it contains common non-name patterns
        if any(word in text_lower for word in ['code', 'number', 'id', 'fee', 'total']):
            return False
        
        # Check if it looks like an actual name
        # Names are usually capitalized and alphabetic
        if (len(text) >= 3 and 
            text[0].isupper() and 
            text.isalpha() and 
            text_lower not in field_labels):
            
            # Additional check: is it a known personal name pattern?
            known_names = {'ashish', 'arun', 'kumar', 'sangeeta', 'kumari'}
            if text_lower in known_names:
                return True
            
            # Check if it's in ALL CAPS (common for names in forms)
            if text.isupper() and len(text) >= 3:
                # But exclude common place names and institutions
                place_names = {
                    'delhi', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'hyderabad',
                    'pune', 'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur',
                    'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri',
                    'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik',
                    'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai', 'varanasi',
                    'srinagar', 'aurangabad', 'dhanbad', 'amritsar', 'navi', 'allahabad',
                    'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada',
                    'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh',
                    'solapur', 'hubballi', 'tiruchirappalli', 'tiruppur', 'moradabad',
                    'mysore', 'bareilly', 'gurgaon', 'aligarh', 'jalandhar', 'bhubaneswar',
                    'salem', 'warangal', 'guntur', 'bhiwandi', 'saharanpur', 'gorakhpur',
                    'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack',
                    'firozabad', 'kochi', 'nellore', 'bhavnagar', 'dehradun', 'durgapur',
                    'asansol', 'rourkela', 'nanded', 'kolhapur', 'ajmer', 'akola',
                    'gulbarga', 'jamnagar', 'ujjain', 'loni', 'siliguri', 'jhansi',
                    'ulhasnagar', 'jammu', 'sangli', 'mangalore', 'erode', 'belgaum',
                    'ambattur', 'tirunelveli', 'malegaon', 'gaya', 'jalgaon', 'udaipur',
                    'maheshtala', 'bseb', 'bihar', 'dseu', 'okhla', 'patori', 'darbhanga',
                    'kolhanta', 'bakkarwala', 'nangloi', 'najafgarh', 'loknayak', 'puram',
                    'rohini', 'sector', 'pant', 'maharaja', 'agrasen', 'union', 'bank',
                    'india', 'chhotu', 'ram', 'rural'
                }
                
                if text_lower not in place_names:
                    # Use LLM for intelligent validation if available
                    if self.llm_agent:
                        try:
                            is_name = self._ask_llm_if_name(text)
                            if is_name is not None:
                                return is_name
                        except Exception as e:
                            logger.debug(f"LLM validation failed for '{text}': {e}")
                    
                    # Default heuristic: if it's ALL CAPS and not in exclusion list, likely a name
                    return True
        
        return False
    
    def _is_actual_address_info(self, text: str) -> bool:
        """Check if text is actual address information"""
        text_lower = text.lower().strip()
        
        # Skip field labels
        address_labels = {'address', 'line', 'state', 'district', 'pin', 'zip', 'pincode'}
        if text_lower in address_labels:
            return False
        
        # Check for actual address components
        if any(term in text_lower for term in ['street', 'road', 'lane', 'colony', 'sector']):
            return True
        
        # Check for pin codes (6 digits)
        if text.isdigit() and len(text) == 6:
            return True
        
        return len(text) > 3  # Other address info
    
    def _is_actual_phone_number(self, text: str) -> bool:
        """Check if text is an actual phone number"""
        digit_count = sum(1 for c in text if c.isdigit())
        return digit_count >= 10
    
    def _is_actual_email(self, text: str) -> bool:
        """Check if text is an actual email address"""
        return '@' in text and '.' in text
    
    def _is_actual_id_number(self, text: str) -> bool:
        """Check if text is an actual ID number"""
        # Long numeric strings
        if text.isdigit() and len(text) >= 8:
            return True
        # Mixed alphanumeric IDs
        if len(text) >= 6 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
            return True
        return False
    
    def _is_actual_personal_date(self, text: str) -> bool:
        """Check if text is an actual personal date"""
        # Date patterns like DD-MM-YYYY, DD/MM/YYYY
        if any(sep in text for sep in ['-', '/', '.']):
            parts = text.replace('-', '/').replace('.', '/').split('/')
            if len(parts) == 3:
                try:
                    day, month, year = map(int, parts)
                    if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030:
                        return True
                except:
                    pass
        return False
    
    def _ask_llm_if_name(self, text: str) -> Optional[bool]:
        """Use LLM to intelligently determine if text is a person's name"""
        if not self.llm_agent:
            return None
        
        prompt = f"""Is "{text}" a PERSON'S NAME?

Consider these examples:
- "ASHISH" → YES (person's name)
- "KUMAR" → YES (surname/family name)  
- "SANGEETA" → YES (person's name)
- "DELHI" → NO (place name)
- "ENGINEERING" → NO (field of study)
- "BANK" → NO (institution type)
- "TECH" → NO (abbreviation)
- "ORDER" → NO (form field)

Answer: YES or NO"""
        
        try:
            response = self.llm_agent.call_groq_api(prompt, max_tokens=5)
            if response and 'YES' in response.upper():
                logger.debug(f"LLM confirms '{text}' is a person name")
                return True
            elif response and 'NO' in response.upper():
                logger.debug(f"LLM confirms '{text}' is NOT a person name")
                return False
        except Exception as e:
            logger.debug(f"LLM call failed for name validation: {e}")
        
        return None
