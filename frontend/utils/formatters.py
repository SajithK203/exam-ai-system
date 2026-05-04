"""
Data Formatters - Format data for display in UI.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataFormatters:
    """Format data for UI display."""
    
    @staticmethod
    def format_question(question):
        """Format question for display."""
        try:
            return {
                'id': question.get('id'),
                'text': question.get('question_text', '')[:200] + '...',
                'full_text': question.get('question_text', ''),
                'type': question.get('question_type', 'Unknown'),
                'topic': question.get('topic_name', 'Unclassified'),
                'marks': question.get('marks_allocated', 0),
                'year': question.get('year', 'N/A'),
                'difficulty': question.get('difficulty_level', 'Medium')
            }
        except Exception as e:
            logger.error(f"Error formatting question: {e}")
            return None
    
    @staticmethod
    def format_topic_frequency(topics):
        """Format topic frequency data."""
        try:
            return [
                {
                    'topic': t.get('topic_name', 'Unknown'),
                    'frequency': t.get('frequency', 0),
                    'percentage': None  # Will calculate later if needed
                }
                for t in topics
            ]
        except Exception as e:
            logger.error(f"Error formatting topic frequency: {e}")
            return []
    
    @staticmethod
    def format_paper_info(paper):
        """Format paper information."""
        try:
            return {
                'id': paper.get('id'),
                'subject': paper.get('subject', 'Unknown'),
                'year': paper.get('year', 'N/A'),
                'exam_type': paper.get('exam_type', 'N/A'),
                'title': paper.get('exam_title', 'Untitled'),
                'questions': paper.get('total_questions', 0),
                'uploaded': paper.get('upload_date', 'N/A'),
                'processed': 'Yes' if paper.get('is_processed') else 'No',
                'file_size_mb': round(paper.get('file_size', 0) / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Error formatting paper: {e}")
            return None
    
    @staticmethod
    def format_date(date_obj, format_string="%Y-%m-%d"):
        """Format date object."""
        try:
            if isinstance(date_obj, str):
                return date_obj
            
            if date_obj:
                return date_obj.strftime(format_string)
            
            return "N/A"
        except Exception as e:
            logger.warning(f"Error formatting date: {e}")
            return "N/A"
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size for display."""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ("B", "KB", "MB", "GB")
            i = 0
            
            while size_bytes >= 1024 and i < len(size_names) - 1:
                size_bytes /= 1024
                i += 1
            
            return f"{size_bytes:.2f} {size_names[i]}"
        except Exception as e:
            logger.warning(f"Error formatting file size: {e}")
            return "Unknown"
    
    @staticmethod
    def format_percentage(value, total):
        """Format value as percentage."""
        try:
            if total == 0:
                return 0
            
            return round((value / total) * 100, 2)
        except Exception as e:
            logger.warning(f"Error formatting percentage: {e}")
            return 0
    
    @staticmethod
    def format_statistics(stats):
        """Format statistics for display."""
        try:
            return {
                'total_papers': stats.get('total_papers', 0),
                'total_questions': stats.get('total_questions', 0),
                'unique_topics': stats.get('unique_topics', 0),
                'avg_marks': round(stats.get('avg_marks', 0), 2),
                'years_covered': stats.get('years_covered', 0)
            }
        except Exception as e:
            logger.error(f"Error formatting statistics: {e}")
            return {}
    
    @staticmethod
    def truncate_text(text, max_length=100):
        """Truncate text to max length."""
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text
    
    @staticmethod
    def format_difficulty_badge(difficulty):
        """Format difficulty level with color."""
        badges = {
            'Easy': '🟢 Easy',
            'Medium': '🟡 Medium',
            'Hard': '🔴 Hard'
        }
        return badges.get(difficulty, '⚪ Unknown')
    
    @staticmethod
    def format_question_type_badge(question_type):
        """Format question type with icon."""
        badges = {
            'Multiple Choice': '📌 MCQ',
            'Short Answer': '📝 Short',
            'Long Answer': '📄 Long',
            'Practical': '💻 Practical'
        }
        return badges.get(question_type, '❓ Unknown')
