"""
Validators - Input validation utilities.
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_pdf_file(file_path):
        """Validate if file is a valid PDF."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
            
            if file_path.suffix.lower() != '.pdf':
                return False
            
            # Check magic number for PDF files
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        
        except Exception as e:
            logger.warning(f"PDF validation error: {e}")
            return False
    
    @staticmethod
    def validate_subject_name(subject):
        """Validate subject name."""
        if not subject or len(subject) < 2:
            return False
        
        if len(subject) > 100:
            return False
        
        # Allow alphanumeric, spaces, hyphens
        pattern = r'^[a-zA-Z0-9\s\-]+$'
        return re.match(pattern, subject) is not None
    
    @staticmethod
    def validate_year(year):
        """Validate exam year."""
        try:
            year = int(year)
            return 1990 <= year <= 2030
        except:
            return False
    
    @staticmethod
    def validate_file_size(file_size, max_size):
        """Validate file size."""
        return 0 < file_size <= max_size
    
    @staticmethod
    def validate_question_text(text):
        """Validate question text."""
        if not text or len(text) < 10:
            return False
        
        if len(text) > 10000:
            return False
        
        return True
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """Validate integer input."""
        try:
            value = int(value)
            
            if min_val is not None and value < min_val:
                return False
            
            if max_val is not None and value > max_val:
                return False
            
            return True
        except:
            return False
    
    @staticmethod
    def sanitize_input(text):
        """Remove potentially dangerous characters."""
        if not text:
            return ""
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Remove SQL injection attempts
        dangerous_patterns = ['--', '/*', '*/', 'xp_', 'sp_']
        for pattern in dangerous_patterns:
            text = text.replace(pattern, '')
        
        return text.strip()
