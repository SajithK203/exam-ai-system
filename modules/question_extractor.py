"""
Question Extractor Module - Extract individual questions from text.
Uses regex patterns to identify and parse questions.
Fully extracts MCQ options per question for storage.
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
        r'(\d+\.|[A-Z]\.|i\.|a\))\s+(.+?)(?=(?:\d+\.|[A-Z]\.|i\.|a\))|$)',
        r'^\s*(.+?[?!])\s*$',
    ]

    MCQ_OPTION_RE = re.compile(
        r'(?:^|\n)\s*\(?([A-Da-d])\s*[\)\.\:\-]\s*(.+?)(?=\n\s*\(?[A-Da-d][\)\.\:\-]|$)',
        re.DOTALL
    )

    @staticmethod
    def extract_questions(text, min_length=None):
        """
        Extract questions from text using pattern matching with fallback methods.

        Args:
            text: Cleaned text from PDF
            min_length: Minimum question length (chars)

        Returns:
            List of extracted questions (plain strings)
        """
        min_length = min_length or PDF_CONFIG.get("min_question_length", 20)

        try:
            questions = []

            numbered_questions = QuestionExtractor._extract_numbered_questions(text)
            if numbered_questions:
                questions.extend(numbered_questions)
                logger.debug(f"Numbered pattern found {len(numbered_questions)} questions")

            if len(questions) < 5:
                lettered_questions = QuestionExtractor._extract_lettered_questions(text)
                if lettered_questions:
                    questions.extend(lettered_questions)
                    logger.debug(f"Lettered pattern found {len(lettered_questions)} questions")

            if len(questions) < 3:
                fallback_questions = QuestionExtractor._extract_by_question_marks(text)
                if fallback_questions:
                    questions.extend(fallback_questions)
                    logger.debug(f"Question mark fallback found {len(fallback_questions)} questions")

            if len(questions) == 0:
                fallback_questions = QuestionExtractor._extract_by_delimiters(text)
                if fallback_questions:
                    questions.extend(fallback_questions)
                    logger.debug(f"Delimiter fallback found {len(fallback_questions)} questions")

            questions = [q.strip() for q in questions if len(q.strip()) >= min_length]
            questions = list(dict.fromkeys(questions))

            logger.info(f"Extracted {len(questions)} questions from text (min_length={min_length})")
            return questions

        except Exception as e:
            logger.error(f"Error extracting questions: {e}")
            raise

    @staticmethod
    def _extract_numbered_questions(text):
        """Extract questions using numbered pattern (Q1, Q2, Question 1, etc.)"""
        questions = []
        pattern = r'(?:^|\n)Q\s*\.?\s*(\d+)\s*[\.:]\s*(.+?)(?=(?:^|\n)Q\s*\.?\s*\d+|$)'
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            question_text = match.group(2).strip()
            question_text = QuestionExtractor._isolate_question_text(question_text)
            if question_text:
                questions.append(question_text)
        return questions

    @staticmethod
    def _extract_lettered_questions(text):
        """Extract questions using lettered pattern (A), B), etc.)"""
        questions = []
        pattern = r'(?:^|\n)\s*([A-Z]\s*[\)\.:])\\s+(.+?)(?=(?:^|\n)[A-Z][\)\.]|$)'
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
            parts = re.split(r'\n\s*[A-Da-d][\s\)\.:]\s', text)
            if parts:
                question = parts[0].strip()
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
            pattern = r'([^.!?]*\?)'
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                question = match.group(1).strip()
                if len(question) > 20:
                    questions.append(question)
        except Exception as e:
            logger.warning(f"Error in question mark extraction: {e}")
        return questions

    @staticmethod
    def _extract_by_delimiters(text):
        """Fallback: Split text by common delimiters."""
        questions = []
        try:
            delimiter_pattern = r'(?:^|\n)\s*(?:Q\.?|Question)\s*\d+[\.:]*\s*|\n(?=\S)'
            parts = re.split(delimiter_pattern, text)

            for part in parts:
                if not part.strip():
                    continue
                lines = part.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) < 20 or line.isupper():
                        continue
                    clean_line = re.sub(r'^[A-Da-d][\)\.\:\-]\s*', '', line)
                    clean_line = re.split(r'\n\s*[A-Da-d][\)\.:]\s', clean_line)[0].strip()
                    if len(clean_line) >= 20 and clean_line not in questions:
                        questions.append(clean_line)
        except Exception as e:
            logger.warning(f"Error in delimiter extraction: {e}")
        return questions

    @staticmethod
    def identify_question_type(question_text):
        """
        Identify the type of question (MCQ, Short Answer, Long Answer, Practical).

        Returns:
            Type as string
        """
        try:
            question_lower = question_text.lower()

            if re.search(r'\(?\s*[a-d]\s*\)', question_text, re.IGNORECASE):
                return "Multiple Choice"

            if re.search(r'\bwrite\b|\bcode\b|\bimplement\b|\bdesign\b|\bdevelop\b|\bprogram\b', question_lower):
                return "Practical"

            words = question_text.split()
            if len(words) <= 20:
                if re.search(r'\bdefine\b|\blist\b|\bname\b|\bstate\b|\bwrite down\b|\bmention\b', question_lower):
                    return "Short Answer"

            return "Long Answer"

        except Exception as e:
            logger.warning(f"Error identifying question type: {e}")
            return "Long Answer"

    @staticmethod
    def extract_options(question_text):
        """
        Extract MCQ options from question text.

        Returns:
            List of dicts: [{'label': 'A', 'text': '...'}, ...]
        """
        try:
            options = []
            # Match A) / B) / A. / A: style options
            pattern = r'(?:^|\n)\s*\(?([A-Da-d])\s*[\)\.\:\-]\s*(.+?)(?=\n\s*\(?[A-Da-d][\)\.\:\-]|$)'
            matches = re.finditer(pattern, question_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)

            seen_labels = set()
            for match in matches:
                label = match.group(1).upper()
                text = match.group(2).strip().replace('\n', ' ')
                if label not in seen_labels and text:
                    options.append({'label': label, 'text': text})
                    seen_labels.add(label)

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
            pattern = r'(?:\(|\[)?\s*(\d+)\s*(?:[Mm]arks?)?(?:\)|\])?'
            matches = re.finditer(pattern, question_text)
            for match in matches:
                marks = int(match.group(1))
                if 1 <= marks <= 50:
                    return marks

            words = len(question_text.split())
            if words < 20:
                return 2
            elif words < 50:
                return 5
            else:
                return 10

        except Exception as e:
            logger.warning(f"Error estimating marks: {e}")
            return 5

    @staticmethod
    def parse_question_full(question_text):
        """
        Parse question completely and return structured data including MCQ options.

        Returns:
            Dictionary with question details:
            {
                'text': str,
                'type': str,
                'options': [{'label': str, 'text': str}],
                'marks': int,
                'word_count': int
            }
        """
        try:
            q_type = QuestionExtractor.identify_question_type(question_text)
            options = QuestionExtractor.extract_options(question_text) if q_type == "Multiple Choice" else []

            # Strip options block from question text for clean storage
            clean_text = question_text
            if options:
                # Remove everything from first option onward
                first_opt_match = re.search(
                    r'\n\s*\(?[A-Da-d][\)\.\:\-]\s+', question_text
                )
                if first_opt_match:
                    clean_text = question_text[:first_opt_match.start()].strip()

            return {
                'text': clean_text.strip(),
                'type': q_type,
                'options': options,
                'marks': QuestionExtractor.estimate_marks(question_text),
                'word_count': len(clean_text.split()),
            }
        except Exception as e:
            logger.error(f"Error parsing question: {e}")
            raise
