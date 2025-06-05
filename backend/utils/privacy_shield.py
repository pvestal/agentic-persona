"""
Privacy Shield implementation for PII detection and filtering
Allows all AI APIs while protecting sensitive data
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional, Set
from datetime import datetime
import hashlib
from functools import lru_cache

from backend.config import settings
from backend.database.models import PrivacyShieldLog
from backend.database.connection import db_manager

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detects various types of PII in text and structured data"""
    
    # Regex patterns for common PII
    PATTERNS = {
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
        'credit_card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
        'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        'date_of_birth': re.compile(r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b'),
        'passport': re.compile(r'\b[A-Z]{1,2}[0-9]{6,9}\b'),
        'driver_license': re.compile(r'\b[A-Z]{1,2}[0-9]{5,8}\b'),
        'bank_account': re.compile(r'\b[0-9]{8,17}\b'),
        'medicare': re.compile(r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}[A-Z]\b'),
    }
    
    # Keywords that might indicate PII context
    PII_KEYWORDS = {
        'personal': ['name', 'address', 'birthdate', 'age', 'gender', 'ethnicity'],
        'financial': ['account', 'balance', 'credit', 'debit', 'bank', 'routing'],
        'medical': ['diagnosis', 'prescription', 'medical', 'health', 'patient'],
        'identification': ['license', 'passport', 'ssn', 'identification', 'id number'],
    }
    
    def __init__(self):
        self.detection_stats = {
            'total_scanned': 0,
            'pii_found': 0,
            'types_found': {}
        }
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text and return findings by type"""
        findings = {}
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                findings[pii_type] = matches
                self.detection_stats['types_found'][pii_type] = \
                    self.detection_stats['types_found'].get(pii_type, 0) + len(matches)
        
        # Check for potential names (simple heuristic)
        if self._contains_potential_name(text):
            findings['potential_name'] = ['<name_detected>']
        
        self.detection_stats['total_scanned'] += 1
        if findings:
            self.detection_stats['pii_found'] += 1
            
        return findings
    
    def _contains_potential_name(self, text: str) -> bool:
        """Simple heuristic to detect potential names"""
        # Look for patterns like "Mr./Mrs./Dr. LastName" or "FirstName LastName"
        name_patterns = [
            r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def scan_dict(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Recursively scan dictionary for PII"""
        all_findings = {}
        
        def scan_value(value: Any, key: str = '') -> None:
            if isinstance(value, str):
                findings = self.detect_pii(value)
                if findings:
                    for pii_type, matches in findings.items():
                        if pii_type not in all_findings:
                            all_findings[pii_type] = []
                        all_findings[pii_type].extend(matches)
            elif isinstance(value, dict):
                for k, v in value.items():
                    scan_value(v, k)
            elif isinstance(value, list):
                for item in value:
                    scan_value(item, key)
        
        scan_value(data)
        return all_findings


class PrivacyShield:
    """Main privacy shield for filtering PII while allowing AI API access"""
    
    def __init__(self):
        self.detector = PIIDetector()
        self.enabled = settings.PRIVACY_SHIELD_ENABLED
        self.confidence_threshold = settings.PII_DETECTION_CONFIDENCE
        self._replacement_cache = {}
        
    def filter_request(self, data: Any, request_id: str = None) -> Tuple[Any, Dict[str, Any]]:
        """Filter PII from outgoing requests to AI APIs"""
        if not self.enabled:
            return data, {"filtered": False, "reason": "disabled"}
        
        start_time = datetime.utcnow()
        original_size = len(json.dumps(data)) if data else 0
        
        # Detect PII
        if isinstance(data, dict):
            pii_findings = self.detector.scan_dict(data)
        elif isinstance(data, str):
            pii_findings = self.detector.detect_pii(data)
        else:
            pii_findings = {}
        
        # Filter data if PII found
        if pii_findings:
            filtered_data = self._filter_data(data, pii_findings)
            filtered_size = len(json.dumps(filtered_data)) if filtered_data else 0
        else:
            filtered_data = data
            filtered_size = original_size
        
        # Log the filtering operation
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        filter_log = {
            "filtered": bool(pii_findings),
            "pii_types": list(pii_findings.keys()),
            "original_size": original_size,
            "filtered_size": filtered_size,
            "processing_time_ms": processing_time,
            "request_id": request_id
        }
        
        # Async log to database (fire and forget)
        if pii_findings and request_id:
            self._log_filtering_async(request_id, "request", filter_log)
        
        return filtered_data, filter_log
    
    def filter_response(self, data: Any, request_id: str = None) -> Tuple[Any, Dict[str, Any]]:
        """Filter PII from incoming responses from AI APIs"""
        # Similar to filter_request but for responses
        return self.filter_request(data, request_id)
    
    def _filter_data(self, data: Any, pii_findings: Dict[str, List[str]]) -> Any:
        """Replace PII with safe placeholders"""
        if isinstance(data, str):
            filtered = data
            for pii_type, matches in pii_findings.items():
                for match in matches:
                    placeholder = self._get_placeholder(match, pii_type)
                    filtered = filtered.replace(match, placeholder)
            return filtered
            
        elif isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if isinstance(value, str):
                    filtered_value = value
                    for pii_type, matches in pii_findings.items():
                        for match in matches:
                            if match in value:
                                placeholder = self._get_placeholder(match, pii_type)
                                filtered_value = filtered_value.replace(match, placeholder)
                    filtered[key] = filtered_value
                elif isinstance(value, (dict, list)):
                    filtered[key] = self._filter_data(value, pii_findings)
                else:
                    filtered[key] = value
            return filtered
            
        elif isinstance(data, list):
            return [self._filter_data(item, pii_findings) for item in data]
            
        return data
    
    def _get_placeholder(self, pii_value: str, pii_type: str) -> str:
        """Generate consistent placeholder for PII value"""
        # Use cache for consistent replacements
        cache_key = f"{pii_type}:{pii_value}"
        if cache_key in self._replacement_cache:
            return self._replacement_cache[cache_key]
        
        # Generate placeholder
        if pii_type == 'email':
            placeholder = f"[EMAIL_{self._hash_value(pii_value)[:8]}]"
        elif pii_type == 'phone':
            placeholder = f"[PHONE_{self._hash_value(pii_value)[:8]}]"
        elif pii_type == 'ssn':
            placeholder = f"[SSN_{self._hash_value(pii_value)[:8]}]"
        elif pii_type == 'credit_card':
            placeholder = f"[CC_{self._hash_value(pii_value)[:8]}]"
        else:
            placeholder = f"[{pii_type.upper()}_{self._hash_value(pii_value)[:8]}]"
        
        self._replacement_cache[cache_key] = placeholder
        return placeholder
    
    def _hash_value(self, value: str) -> str:
        """Generate hash of PII value for consistent placeholders"""
        return hashlib.sha256(value.encode()).hexdigest()
    
    def _log_filtering_async(self, request_id: str, data_type: str, filter_log: Dict[str, Any]):
        """Log filtering operation to database (async)"""
        try:
            # This would be called in an async context in production
            logger.info(f"Privacy shield filtered {data_type}: {filter_log}")
        except Exception as e:
            logger.error(f"Failed to log privacy shield operation: {e}")
    
    def validate_api_endpoint(self, url: str) -> bool:
        """Validate if API endpoint is allowed"""
        # Extract domain from URL
        domain_pattern = re.compile(r'https?://([^/]+)')
        match = domain_pattern.match(url)
        
        if not match:
            return False
        
        domain = match.group(1).lower()
        
        # Check against allowed domains
        for allowed_domain in settings.ALLOWED_EXTERNAL_APIS:
            if allowed_domain in domain or domain in allowed_domain:
                return True
        
        logger.warning(f"API endpoint not in allowed list: {domain}")
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get privacy shield statistics"""
        return {
            "enabled": self.enabled,
            "detection_stats": self.detector.detection_stats,
            "cache_size": len(self._replacement_cache),
            "allowed_apis": settings.ALLOWED_EXTERNAL_APIS
        }


# Global privacy shield instance
privacy_shield = PrivacyShield()