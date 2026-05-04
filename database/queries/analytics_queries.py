"""
Analytics query operations - SQL queries for pattern analysis and insights.
"""

from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class AnalyticsQueries:
    """Handle all analytics and reporting queries."""
    
    @staticmethod
    def get_topic_frequency(subject=None, years=None):
        """Get topic frequency distribution."""
        if subject:
            query = """
                SELECT t.topic_name, COUNT(q.id) as frequency
                FROM questions q
                LEFT JOIN topics t ON q.topic_id = t.id
                JOIN papers p ON q.paper_id = p.id
                WHERE p.subject = %s
                GROUP BY q.topic_id, t.topic_name
                ORDER BY frequency DESC
            """
            if years:
                query += " AND p.year IN ({})".format(','.join(['%s']*len(years)))
                params = [subject] + years
            else:
                params = [subject]
        else:
            query = """
                SELECT t.topic_name, COUNT(q.id) as frequency
                FROM questions q
                LEFT JOIN topics t ON q.topic_id = t.id
                GROUP BY q.topic_id, t.topic_name
                ORDER BY frequency DESC
            """
            params = []
        
        try:
            result = DatabaseConnection.execute_query(query, params or None, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching topic frequency: {e}")
            raise
    
    @staticmethod
    def get_trending_topics(subject, years=5):
        """Get trending topics over years."""
        query = """
            SELECT 
                t.topic_name,
                p.year,
                COUNT(q.id) as frequency
            FROM questions q
            LEFT JOIN topics t ON q.topic_id = t.id
            JOIN papers p ON q.paper_id = p.id
            WHERE p.subject = %s 
            AND p.year >= (SELECT MAX(year) - %s FROM papers)
            GROUP BY p.year, q.topic_id, t.topic_name
            ORDER BY p.year DESC, frequency DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, (subject, years), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching trending topics: {e}")
            raise
    
    @staticmethod
    def get_top_topics(subject, limit=10):
        """Get top N most frequent topics."""
        query = """
            SELECT t.topic_name, COUNT(q.id) as frequency
            FROM questions q
            LEFT JOIN topics t ON q.topic_id = t.id
            JOIN papers p ON q.paper_id = p.id
            WHERE p.subject = %s
            GROUP BY q.topic_id, t.topic_name
            ORDER BY frequency DESC
            LIMIT %s
        """
        try:
            result = DatabaseConnection.execute_query(query, (subject, limit), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching top topics: {e}")
            raise
    
    @staticmethod
    def get_repeated_questions():
        """Get questions that appear in multiple papers."""
        query = """
            SELECT 
                q.question_text,
                t.topic_name,
                COUNT(DISTINCT q.paper_id) as paper_count,
                COUNT(q.id) as total_occurrences
            FROM questions q
            LEFT JOIN topics t ON q.topic_id = t.id
            GROUP BY LOWER(q.question_text)
            HAVING paper_count > 1
            ORDER BY paper_count DESC, total_occurrences DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching repeated questions: {e}")
            raise
    
    @staticmethod
    def get_question_type_distribution(subject=None):
        """Get distribution of question types."""
        if subject:
            query = """
                SELECT 
                    q.question_type,
                    COUNT(q.id) as count,
                    ROUND(COUNT(q.id) * 100 / (SELECT COUNT(*) FROM questions WHERE paper_id IN 
                        (SELECT id FROM papers WHERE subject = %s)), 2) as percentage
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                WHERE p.subject = %s
                GROUP BY q.question_type
                ORDER BY count DESC
            """
            params = [subject, subject]
        else:
            query = """
                SELECT 
                    question_type,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM questions), 2) as percentage
                FROM questions
                GROUP BY question_type
                ORDER BY count DESC
            """
            params = []
        
        try:
            result = DatabaseConnection.execute_query(query, params or None, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching question type distribution: {e}")
            raise
    
    @staticmethod
    def get_difficulty_distribution(subject=None):
        """Get distribution of difficulty levels."""
        if subject:
            query = """
                SELECT 
                    q.difficulty_level,
                    COUNT(q.id) as count
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                WHERE p.subject = %s
                GROUP BY q.difficulty_level
                ORDER BY FIELD(q.difficulty_level, 'Easy', 'Medium', 'Hard')
            """
            params = [subject]
        else:
            query = """
                SELECT difficulty_level, COUNT(*) as count
                FROM questions
                GROUP BY difficulty_level
                ORDER BY FIELD(difficulty_level, 'Easy', 'Medium', 'Hard')
            """
            params = []
        
        try:
            result = DatabaseConnection.execute_query(query, params or None, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching difficulty distribution: {e}")
            raise
    
    @staticmethod
    def get_papers_per_year(subject=None):
        """Get count of papers per year."""
        if subject:
            query = """
                SELECT year, COUNT(*) as paper_count, COUNT(DISTINCT exam_type) as exam_types
                FROM papers
                WHERE subject = %s
                GROUP BY year
                ORDER BY year DESC
            """
            params = [subject]
        else:
            query = """
                SELECT year, COUNT(*) as paper_count
                FROM papers
                GROUP BY year
                ORDER BY year DESC
            """
            params = []
        
        try:
            result = DatabaseConnection.execute_query(query, params or None, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching papers per year: {e}")
            raise
    
    @staticmethod
    def get_subject_statistics():
        """Get statistics for all subjects."""
        query = """
            SELECT 
                p.subject,
                COUNT(DISTINCT p.id) as total_papers,
                COUNT(q.id) as total_questions,
                COUNT(DISTINCT p.year) as years_covered,
                ROUND(COUNT(q.id) / COUNT(DISTINCT p.id), 2) as avg_questions_per_paper,
                MIN(p.year) as earliest_year,
                MAX(p.year) as latest_year
            FROM papers p
            LEFT JOIN questions q ON p.id = q.paper_id
            GROUP BY p.subject
            ORDER BY total_questions DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching subject statistics: {e}")
            raise
    
    @staticmethod
    def get_topic_trend_analysis(subject, topic_id, years=10):
        """Get trend analysis for a specific topic."""
        query = """
            SELECT 
                p.year,
                COUNT(q.id) as frequency,
                SUM(q.marks_allocated) as total_marks
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            WHERE p.subject = %s 
            AND q.topic_id = %s
            AND p.year >= (SELECT MAX(year) - %s FROM papers)
            GROUP BY p.year
            ORDER BY p.year ASC
        """
        try:
            result = DatabaseConnection.execute_query(query, (subject, topic_id, years), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching topic trend analysis: {e}")
            raise
    
    @staticmethod
    def get_question_statistics():
        """Get overall question statistics."""
        query = """
            SELECT 
                COUNT(DISTINCT id) as total_questions,
                COUNT(DISTINCT paper_id) as papers_covered,
                COUNT(DISTINCT topic_id) as unique_topics,
                ROUND(AVG(marks_allocated), 2) as avg_marks,
                SUM(marks_allocated) as total_marks_in_system
            FROM questions
        """
        try:
            result = DatabaseConnection.execute_query(query, fetch_one=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching question statistics: {e}")
            raise
