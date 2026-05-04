"""
Text Cleaning Module - Clean and preprocess extracted PDF text.
Handles text normalization, removing noise, formatting.
"""

import re
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Handle text cleaning and preprocessing."""
    
    @staticmethod
    def clean_text(text):
        """
        Clean raw extracted text from PDF.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        try:
            if not text or not isinstance(text, str):
                return ""
            
            # Remove multiple newlines and replace with single newline
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            # Remove leading/trailing whitespace from each line
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(lines)
            
            # Remove special characters but keep hyphens, periods, colons
            text = re.sub(r'[^\w\s\n\.\,\-\:\;\(\)\[\]\?\!\'\"\/\+\=\<\>]', '', text)
            
            # Remove excessive spaces
            text = re.sub(r' +', ' ', text)
            
            # Remove page breaks and headers
            text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
            
            logger.debug("Text cleaning completed")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            raise
    
    @staticmethod
    def normalize_whitespace(text):
        """Remove extra whitespace while preserving structure."""
        try:
            # Replace multiple spaces with single space
            text = re.sub(r' +', ' ', text)
            
            # Replace multiple newlines with double newline
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error normalizing whitespace: {e}")
            raise
    
    @staticmethod
    def remove_special_characters(text, keep_chars=None):
        """
        Remove special characters from text.
        
        Args:
            text: Input text
            keep_chars: String of characters to keep (in addition to alphanumeric)
        """
        try:
            if keep_chars is None:
                keep_chars = r'\s\.\,\-\?\!'  # Default chars to keep
            
            pattern = f'[^a-zA-Z0-9{keep_chars}]'
            text = re.sub(pattern, '', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error removing special characters: {e}")
            raise
    
    @staticmethod
    def extract_lines(text):
        """
        Extract lines from text and remove empty ones.
        
        Returns:
            List of non-empty lines
        """
        try:
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            return lines
        except Exception as e:
            logger.error(f"Error extracting lines: {e}")
            raise
    
    @staticmethod
    def remove_page_markers(text):
        """Remove page numbers and markers."""
        try:
            # Remove page number patterns like "Page 1", "P. 1", etc.
            text = re.sub(r'[Pp]age\s*\d+', '', text)
            text = re.sub(r'[Pp]\.?\s*\d+', '', text)
            
            # Remove horizontal lines (often used as page separators)
            text = re.sub(r'[\-_]{5,}', '', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error removing page markers: {e}")
            raise
    
    @staticmethod
    def merge_split_words(text):
        """Merge words that were split across lines."""
        try:
            # This regex finds words broken with hyphen at line end
            text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
            return text.strip()
        except Exception as e:
            logger.error(f"Error merging split words: {e}")
            raise
    
    @staticmethod
    def standardize_spacing(text):
        """Standardize spacing around punctuation."""
        try:
            # Add space before question mark/exclamation if missing
            text = re.sub(r'(\w)([?!])', r'\1 \2', text)
            
            # Add space after question mark/exclamation if missing
            text = re.sub(r'([?!])(\w)', r'\1 \2', text)
            
            # Remove space before comma/period
            text = re.sub(r'\s+([,.])', r'\1', text)
            
            # Add space after comma/period if missing
            text = re.sub(r'([,.])(\w)', r'\1 \2', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error standardizing spacing: {e}")
            raise
    
    @staticmethod
    def full_clean(text):
        """
        Apply all cleaning operations.
        
        Returns:
            Fully cleaned text
        """
        try:
            text = TextCleaner.clean_text(text)
            text = TextCleaner.remove_page_markers(text)
            text = TextCleaner.merge_split_words(text)
            text = TextCleaner.normalize_whitespace(text)
            text = TextCleaner.standardize_spacing(text)
            
            logger.info("Full text cleaning completed")
            return text
        except Exception as e:
            logger.error(f"Error in full clean: {e}")
            raise
