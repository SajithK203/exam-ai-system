"""
Question Extractor Module - Extract individual questions from text.
Uses regex patterns to identify and parse questions.
"""

import re
import logging
from config.settings import PDF_CONFIG

logger = logging.getLogger(__name__)


class QuestionExtractor:
    """Extract and parse individual questions from text."""
    
    # Regex patterns for question detection
    QUESTION_PATTERNS = [
        r'(?:Q\.|Q\s*:|Question\s*\d+[:\.]?)\s*(.+?)(?=(?:Q\s*\d+|Question\s*\d+|$))',
        r'(\d+\.|[A-Z]\.|i\.|a\))\s+(.+?)(?=(?:\d+\.|[A-Z]\.|i\.|a\))|$)',  # Numbered/lettered
        r'^\s*(.+?[?!])\s*$',  # Lines ending with question mark
    ]
    
    MCQ_PATTERN = r'\(?\s*[A-D]\s*\)'  # MCQ option markers
    OPTION_PATTERN = r'(?:^\s*|\n\s*)([A-D][\s\)\.:])\s*(.+?)(?=\n[A-D][\s\)\.:]|$)'
    
    @staticmethod
    def extract_questions(text, min_length=None):
        """
        Extract questions from text using pattern matching with fallback methods.
        
        Args:
            text: Cleaned text from PDF
            min_length: Minimum question length (chars)
            
        Returns:
            List of extracted questions
        """
        min_length = min_length or PDF_CONFIG.get("min_question_length", 20)
        
        try:
            questions = []
            
            # Try to extract using numbered pattern (Q1, Q2, etc.)
            numbered_questions = QuestionExtractor._extract_numbered_questions(text)
            if numbered_questions:
                questions.extend(numbered_questions)
                logger.debug(f"Numbered pattern found {len(numbered_questions)} questions")
            
            # Try lettered pattern (A), B), etc.)
            if len(questions) < 5:  # If numbered didn't work well
                lettered_questions = QuestionExtractor._extract_lettered_questions(text)
                if lettered_questions:
                    questions.extend(lettered_questions)
                    logger.debug(f"Lettered pattern found {len(lettered_questions)} questions")
            
            # Fallback: Extract sentences ending with question marks
            if len(questions) < 3:
                fallback_questions = QuestionExtractor._extract_by_question_marks(text)
                if fallback_questions:
                    questions.extend(fallback_questions)
                    logger.debug(f"Question mark fallback found {len(fallback_questions)} questions")
            
            # Final fallback: Split by common delimiters
            if len(questions) == 0:
                fallback_questions = QuestionExtractor._extract_by_delimiters(text)
                if fallback_questions:
                    questions.extend(fallback_questions)
                    logger.debug(f"Delimiter fallback found {len(fallback_questions)} questions")
            
            # Filter by minimum length and remove duplicates
            questions = [q.strip() for q in questions if len(q.strip()) >= min_length]
            questions = list(dict.fromkeys(questions))  # Remove duplicates while preserving order
            
            logger.info(f"Extracted {len(questions)} questions from text (min_length={min_length})")
            return questions
            
        except Exception as e:
            logger.error(f"Error extracting questions: {e}")
            raise
    
    @staticmethod
    def _extract_numbered_questions(text):
        """Extract questions using numbered pattern (Q1, Q2, Question 1, etc.)"""
        questions = []
        
        # Pattern for Q1, Q2, etc.
        pattern = r'(?:^|\n)Q\s*\.?\s*(\d+)\s*[\.:]\s*(.+?)(?=(?:^|\n)Q\s*\.?\s*\d+|$)'
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            question_text = match.group(2).strip()
            # Extract just the question, not the options
            question_text = QuestionExtractor._isolate_question_text(question_text)
            if question_text:
                questions.append(question_text)
        
        return questions
    
    @staticmethod
    def _extract_lettered_questions(text):
        """Extract questions using lettered pattern (A), B), etc.)"""
        questions = []
        
        # Split by letters followed by parenthesis or period
        pattern = r'(?:^|\n)\s*([A-Z]\s*[\)\.:])\s+(.+?)(?=(?:^|\n)[A-Z][\)\.:]|$)'
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            question_text = match.group(2).strip()
            question_text = QuestionExtractor._isolate_question_text(question_text)
            if question_text:
                questions.append(question_text)
        
        return questions
    
    @staticmethod
    def _isolate_question_text(text):
        """Extract just the question part, removing options."""
        try:
            # Split by MCQ option markers
            parts = re.split(r'\n\s*[A-D][\s\)\.:]', text)
            if parts:
                question = parts[0].strip()
                # Remove trailing marks
                question = re.sub(r'\s+[Mm]arks?:\s*\d+\s*$', '', question)
                question = re.sub(r'\s+\(\d+\s*[Mm]arks?\)\s*$', '', question)
                return question
            return text.strip()
        except Exception:
            return text.strip()
    
    @staticmethod
    def _extract_by_question_marks(text):
        """Fallback: Extract sentences ending with question marks."""
        questions = []
        try:
            # Find all sentences ending with ?
            pattern = r'([^.!?]*\?)'
            matches = re.finditer(pattern, text, re.MULTILINE)
            
            for match in matches:
                question = match.group(1).strip()
                if len(question) > 20:  # Filter very short lines
                    questions.append(question)
            
            logger.debug(f"Question mark extraction found {len(questions)} questions")
        except Exception as e:
            logger.warning(f"Error in question mark extraction: {e}")
        
        return questions
    
    @staticmethod
    def _extract_by_delimiters(text):
        """Fallback: Split text by common delimiters and extract potential questions."""
        questions = []
        try:
            # Split by common delimiters
            delimiter_pattern = r'(?:^|\n)\s*(?:Q\.?|Question)\s*\d+[\.:]*\s*|\n(?=\S)'
            parts = re.split(delimiter_pattern, text)
            
            for part in parts:
                if not part.strip():
                    continue
                    
                # Split each part into lines
                lines = part.split('\n')
                for line in lines:
                    line = line.strip()
                    
                    # Skip very short lines and likely headers
                    if len(line) < 20 or line.isupper():
                        continue
                    
                    # Remove option markers from beginning
                    clean_line = re.sub(r'^[A-D][\)\.:\-]\s*', '', line)
                    
                    # Stop at option markers
                    clean_line = re.split(r'\n\s*[A-D][\)\.:]', clean_line)[0].strip()
                    
                    if len(clean_line) >= 20 and clean_line not in questions:
                        questions.append(clean_line)
            
            logger.debug(f"Delimiter extraction found {len(questions)} questions")
        except Exception as e:
            logger.warning(f"Error in delimiter extraction: {e}")
        
        return questions
    
    @staticmethod
    def identify_question_type(question_text):
        """
        Identify the type of question (MCQ, Short Answer, Long Answer).
        
        Returns:
            Type as string: 'Multiple Choice', 'Short Answer', 'Long Answer', 'Practical'
        """
        try:
            question_lower = question_text.lower()
            
            # Check for MCQ indicators
            if re.search(r'\(?\s*[a-d]\s*\)', question_text, re.IGNORECASE):
                return "Multiple Choice"
            
            # Check for practical/practical work
            if re.search(r'write|code|implement|design|develop', question_lower):
                return "Practical"
            
            # Check for short answer (20 words or less, or "define", "list", etc.)
            if len(question_text.split()) <= 20:
                if re.search(r'define|list|name|state|write down|mention', question_lower):
                    return "Short Answer"
            
            # Default to long answer
            return "Long Answer"
            
        except Exception as e:
            logger.warning(f"Error identifying question type: {e}")
            return "Long Answer"
    
    @staticmethod
    def extract_options(question_text):
        """
        Extract MCQ options from question text.
        
        Returns:
            List of dictionaries with option label and text
        """
        try:
            options = []
            
            # Match pattern: A) text, B) text, etc.
            pattern = r'\(?\s*([A-D])\s*[\)\.:\-]\s*(.+?)(?=\([A-D][\)\.:\-]|$)'
            matches = re.finditer(pattern, question_text, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                option_label = match.group(1).upper()
                option_text = match.group(2).strip()
                options.append({
                    'label': option_label,
                    'text': option_text
                })
            
            return options if len(options) >= 2 else []
            
        except Exception as e:
            logger.warning(f"Error extracting options: {e}")
            return []
    
    @staticmethod
    def estimate_marks(question_text):
        """
        Estimate marks allocated to a question.
        
        Returns:
            Integer marks value
        """
        try:
            # Look for patterns like "5 marks", "(5)", "[5 marks]"
            pattern = r'(?:\(|\[)?\s*(\d+)\s*(?:[Mm]arks?)?(?:\)|\])?'
            matches = re.finditer(pattern, question_text)
            
            for match in matches:
                marks = int(match.group(1))
                if 1 <= marks <= 50:  # Reasonable bounds
                    return marks
            
            # Default estimation based on question length
            words = len(question_text.split())
            if words < 20:
                return 2  # Short answer
            elif words < 50:
                return 5  # Medium answer
            else:
                return 10  # Long answer
                
        except Exception as e:
            logger.warning(f"Error estimating marks: {e}")
            return 5  # Default
    
    @staticmethod
    def parse_question_full(question_text):
        """
        Parse question completely and return structured data.
        
        Returns:
            Dictionary with question details
        """
        try:
            return {
                'text': question_text.strip(),
                'type': QuestionExtractor.identify_question_type(question_text),
                'options': QuestionExtractor.extract_options(question_text),
                'marks': QuestionExtractor.estimate_marks(question_text),
                'word_count': len(question_text.split())
            }
        except Exception as e:
            logger.error(f"Error parsing question: {e}")
            raise
