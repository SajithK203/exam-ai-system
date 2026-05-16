"""
PDF Processing Module - Extract text from PDF files.
Uses PyPDF2 for text-based PDFs with graceful OCR fallback for
scanned/image PDFs using pytesseract + pdf2image.
"""

import hashlib
import logging
from pathlib import Path

import PyPDF2
from config.settings import PDF_CONFIG

logger = logging.getLogger(__name__)

# Optional OCR imports — graceful degradation if not installed
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
    logger.info("OCR support available (pytesseract + pdf2image)")
except ImportError:
    OCR_AVAILABLE = False
    logger.warning(
        "OCR libraries not found (pytesseract / pdf2image). "
        "Install them + Tesseract binary for scanned PDF support."
    )


class PDFProcessor:
    """Handle PDF text extraction and processing."""

    # Minimum chars per page to consider text extraction successful
    MIN_TEXT_CHARS = 50

    @staticmethod
    def compute_file_hash(file_bytes: bytes) -> str:
        """Compute MD5 hash of file bytes for duplicate detection."""
        return hashlib.md5(file_bytes).hexdigest()

    @staticmethod
    def extract_text_from_pdf(file_path, timeout=None):
        """
        Extract text from a PDF file.
        Strategy:
            1. Try standard PyPDF2 text extraction.
            2. If result is too short (< MIN_TEXT_CHARS total), attempt OCR.
            3. If OCR unavailable, return whatever was extracted with a warning.

        Args:
            file_path: Path to the PDF file
            timeout: Timeout in seconds (optional, reserved for future use)

        Returns:
            Tuple (extracted_text: str, used_ocr: bool)
        """
        timeout = timeout or PDF_CONFIG.get("extract_text_timeout", 30)
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        # --- Step 1: Standard text extraction ---
        extracted_text = ""
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)
                logger.info(
                    f"Extracting text from PDF ({total_pages} pages): {file_path.name}"
                )

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text() or ""
                        extracted_text += f"\n--- Page {page_num + 1} ---\n"
                        extracted_text += page_text
                    except Exception as e:
                        logger.warning(f"Error on page {page_num + 1}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading PDF with PyPDF2: {e}")
            raise

        meaningful_text = extracted_text.replace("\n", "").replace(" ", "").replace("-", "")
        if len(meaningful_text) >= PDFProcessor.MIN_TEXT_CHARS:
            logger.info(f"Text extraction succeeded: {len(extracted_text)} chars")
            return extracted_text, False  # (text, used_ocr=False)

        # --- Step 2: OCR fallback ---
        logger.info(
            f"Text extraction yielded < {PDFProcessor.MIN_TEXT_CHARS} meaningful chars. "
            "Attempting OCR fallback..."
        )

        if not OCR_AVAILABLE:
            logger.warning(
                "OCR fallback unavailable: pytesseract/pdf2image not installed. "
                "Returning limited text."
            )
            return extracted_text, False

        try:
            ocr_text = PDFProcessor._ocr_extract(file_path)
            if ocr_text.strip():
                logger.info(f"OCR extraction succeeded: {len(ocr_text)} chars")
                return ocr_text, True  # (text, used_ocr=True)
            else:
                logger.warning("OCR returned empty text.")
                return extracted_text, False
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return extracted_text, False

    @staticmethod
    def _ocr_extract(file_path) -> str:
        """
        Convert PDF pages to images and run Tesseract OCR on each page.

        Returns:
            Concatenated OCR text from all pages.
        """
        ocr_text = ""
        try:
            images = convert_from_path(str(file_path), dpi=300)
            logger.info(f"OCR: converted {len(images)} pages to images")

            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img, lang="eng")
                ocr_text += f"\n--- Page {i + 1} (OCR) ---\n"
                ocr_text += page_text
                logger.debug(f"OCR page {i + 1}: {len(page_text)} chars")

        except Exception as e:
            logger.error(f"OCR page processing error: {e}")
            raise

        return ocr_text

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
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "pages": 0,
                "title": "Unknown",
                "author": "Unknown",
            }

            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata["pages"] = len(pdf_reader.pages)

                if pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata.get("/Title", "Unknown")
                    metadata["author"] = pdf_reader.metadata.get("/Author", "Unknown")

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
            if file_path.suffix.lower() != ".pdf":
                return False
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                return len(pdf_reader.pages) > 0
        except Exception as e:
            logger.warning(f"PDF validation failed: {e}")
            return False
