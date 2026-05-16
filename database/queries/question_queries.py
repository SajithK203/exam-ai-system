"""
Question query operations - CRUD operations for exam questions.
"""

from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class QuestionQueries:
    """Handle all question-related database operations."""
    
    @staticmethod
    def create_question(paper_id, question_text, topic_id, question_type, marks=0, difficulty='Medium'):
        """Create a new question record."""
        query = """
            INSERT INTO questions 
            (paper_id, question_text, topic_id, question_type, marks_allocated, difficulty_level)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (paper_id, question_text, topic_id, question_type, marks, difficulty)
        try:
            DatabaseConnection.execute_query(query, params)
            logger.info(f"Question created for paper {paper_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            raise
    
    @staticmethod
    def get_question_by_id(question_id):
        """Get question details by ID."""
        query = "SELECT * FROM questions WHERE id = %s"
        try:
            result = DatabaseConnection.execute_query(query, (question_id,), fetch_one=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching question: {e}")
            raise
    
    @staticmethod
    def get_questions_by_paper(paper_id):
        """Get all questions for a paper."""
        query = """
            SELECT q.*, t.topic_name 
            FROM questions q
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE q.paper_id = %s
            ORDER BY q.created_at
        """
        try:
            result = DatabaseConnection.execute_query(query, (paper_id,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching questions by paper: {e}")
            raise
    
    @staticmethod
    def get_questions_by_topic(topic_id, limit=None):
        """Get all questions for a topic."""
        if limit:
            query = """
                SELECT q.*, p.subject, p.year 
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                WHERE q.topic_id = %s
                ORDER BY p.year DESC, q.created_at DESC
                LIMIT %s
            """
            result = DatabaseConnection.execute_query(query, (topic_id, limit), fetch_all=True)
        else:
            query = """
                SELECT q.*, p.subject, p.year 
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                WHERE q.topic_id = %s
                ORDER BY p.year DESC
            """
            result = DatabaseConnection.execute_query(query, (topic_id,), fetch_all=True)
        try:
            return result
        except Exception as e:
            logger.error(f"Error fetching questions by topic: {e}")
            raise
    
    @staticmethod
    def get_questions_by_subject(subject):
        """Get all questions for a subject."""
        query = """
            SELECT q.*, p.year, t.topic_name
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE p.subject = %s
            ORDER BY p.year DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, (subject,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching questions by subject: {e}")
            raise
    
    @staticmethod
    def get_questions_by_type(question_type):
        """Get all questions of a specific type."""
        query = """
            SELECT * FROM questions 
            WHERE question_type = %s
            ORDER BY created_at DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, (question_type,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching questions by type: {e}")
            raise
    
    @staticmethod
    def search_questions(search_text):
        """Search questions using full-text search."""
        query = """
            SELECT q.*, p.subject, p.year, t.topic_name
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE MATCH(q.question_text) AGAINST(%s IN BOOLEAN MODE)
            ORDER BY p.year DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, (search_text,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            raise
    
    @staticmethod
    def update_question_topic(question_id, topic_id):
        """Update question's topic classification."""
        query = "UPDATE questions SET topic_id = %s WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (topic_id, question_id))
            logger.info(f"Question {question_id} topic updated")
            return True
        except Exception as e:
            logger.error(f"Error updating question topic: {e}")
            raise
    
    @staticmethod
    def increment_frequency(question_id):
        """Increment frequency of a question."""
        query = "UPDATE questions SET frequency = frequency + 1 WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (question_id,))
            return True
        except Exception as e:
            logger.error(f"Error incrementing frequency: {e}")
            raise
    
    @staticmethod
    def get_question_count_by_paper(paper_id):
        """Get total questions count for a paper."""
        query = "SELECT COUNT(*) as count FROM questions WHERE paper_id = %s"
        try:
            result = DatabaseConnection.execute_query(query, (paper_id,), fetch_one=True)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting question count: {e}")
            raise
    
    @staticmethod
    def delete_questions_by_paper(paper_id):
        """Delete all questions for a paper."""
        query = "DELETE FROM questions WHERE paper_id = %s"
        try:
            DatabaseConnection.execute_query(query, (paper_id,))
            logger.info(f"Deleted all questions for paper {paper_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting questions: {e}")
            raise
    
    @staticmethod
    def get_repeated_questions():
        """Get questions that appeared multiple times."""
        query = """
            SELECT 
                MAX(q.id) as id,
                MAX(q.question_text) as question_text,
                q.topic_id,
                q.question_type,
                MAX(q.difficulty_level) as difficulty_level,
                MAX(q.marks_allocated) as marks_allocated,
                p.subject, 
                COUNT(DISTINCT q.paper_id) as appearance_count
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            GROUP BY 
                LOWER(q.question_text),
                q.topic_id,
                q.question_type,
                p.subject
            HAVING appearance_count > 1
            ORDER BY appearance_count DESC
        """
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching repeated questions: {e}")
            raise
    
    @staticmethod
    def get_questions_by_topic_with_subject(subject, topic_name, limit=None):
        """Get questions for a specific topic and subject."""
        if limit:
            query = """
                SELECT q.*, p.subject, p.year, t.topic_name
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                JOIN topics t ON q.topic_id = t.id
                WHERE p.subject = %s AND t.topic_name = %s
                ORDER BY p.year DESC, q.difficulty_level DESC
                LIMIT %s
            """
            result = DatabaseConnection.execute_query(query, (subject, topic_name, limit), fetch_all=True)
        else:
            query = """
                SELECT q.*, p.subject, p.year, t.topic_name
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                JOIN topics t ON q.topic_id = t.id
                WHERE p.subject = %s AND t.topic_name = %s
                ORDER BY p.year DESC, q.difficulty_level DESC
            """
            result = DatabaseConnection.execute_query(query, (subject, topic_name), fetch_all=True)
        
        try:
            return result
        except Exception as e:
            logger.error(f"Error fetching questions by topic and subject: {e}")
            raise
