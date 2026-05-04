"""
PDF Processing Module - Extract text from PDF files.
Uses PyPDF2 for PDF text extraction.
"""

import PyPDF2
from pathlib import Path
import logging
from config.settings import PDF_CONFIG

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF text extraction and processing."""
    
    @staticmethod
    def extract_text_from_pdf(file_path, timeout=None):
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            timeout: Timeout in seconds (optional)
            
        Returns:
            Extracted text as string
        """
        timeout = timeout or PDF_CONFIG.get("extract_text_timeout", 30)
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            if not file_path.suffix.lower() == '.pdf':
                raise ValueError(f"File is not a PDF: {file_path}")
            
            extracted_text = ""
            
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from PDF with {total_pages} pages: {file_path.name}")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text
                        logger.debug(f"Extracted page {page_num + 1}/{total_pages}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue
            
            if not extracted_text.strip():
                logger.warning(f"No text extracted from PDF: {file_path}")
                raise ValueError("PDF appears to be empty or contains only images")
            
            logger.info(f"Successfully extracted text from PDF: {file_path.name}")
            return extracted_text
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    @staticmethod
    def get_pdf_metadata(file_path):
        """
        Extract metadata from PDF file.
        
        Returns:
            Dictionary with metadata (title, author, pages, etc.)
        """
        try:
            file_path = Path(file_path)
            metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'pages': 0,
                'title': 'Unknown',
                'author': 'Unknown'
            }
            
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata['pages'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
                    metadata['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
            
            logger.info(f"PDF metadata extracted: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            raise
    
    @staticmethod
    def validate_pdf(file_path):
        """
        Validate if a file is a valid PDF.
        
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
            
            if file_path.suffix.lower() != '.pdf':
                return False
            
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                return len(pdf_reader.pages) > 0
                
        except Exception as e:
            logger.warning(f"PDF validation failed: {e}")
            return False
