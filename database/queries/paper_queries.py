"""
Paper query operations - CRUD operations for exam papers.
"""

from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class PaperQueries:
    """Handle all paper-related database operations."""
    
    @staticmethod
    def create_paper(subject, exam_title, year, exam_type, file_path, file_size):
        """Create a new paper record."""
        query = """
            INSERT INTO papers (subject, exam_title, year, exam_type, file_path, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (subject, exam_title, year, exam_type, file_path, file_size)
        try:
            DatabaseConnection.execute_query(query, params)
            logger.info(f"Paper created: {subject} - {year}")
            return True
        except Exception as e:
            logger.error(f"Error creating paper: {e}")
            raise
    
    @staticmethod
    def get_paper_by_id(paper_id):
        """Get paper details by ID."""
        query = "SELECT * FROM papers WHERE id = %s"
        try:
            result = DatabaseConnection.execute_query(query, (paper_id,), fetch_one=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching paper: {e}")
            raise
    
    @staticmethod
    def get_all_papers():
        """Get all papers."""
        query = "SELECT * FROM papers ORDER BY upload_date DESC"
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            raise
    
    @staticmethod
    def get_papers_by_subject(subject):
        """Get all papers for a subject."""
        query = "SELECT * FROM papers WHERE subject = %s ORDER BY year DESC"
        try:
            result = DatabaseConnection.execute_query(query, (subject,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching papers by subject: {e}")
            raise
    
    @staticmethod
    def get_papers_by_year(year):
        """Get all papers for a specific year."""
        query = "SELECT * FROM papers WHERE year = %s ORDER BY subject"
        try:
            result = DatabaseConnection.execute_query(query, (year,), fetch_all=True)
            return result
        except Exception as e:
            logger.error(f"Error fetching papers by year: {e}")
            raise
    
    @staticmethod
    def update_paper_status(paper_id, is_processed, total_questions=None):
        """Update paper processing status."""
        if total_questions is not None:
            query = """
                UPDATE papers 
                SET is_processed = %s, total_questions = %s
                WHERE id = %s
            """
            params = (is_processed, total_questions, paper_id)
        else:
            query = "UPDATE papers SET is_processed = %s WHERE id = %s"
            params = (is_processed, paper_id)
        
        try:
            DatabaseConnection.execute_query(query, params)
            logger.info(f"Paper {paper_id} status updated")
            return True
        except Exception as e:
            logger.error(f"Error updating paper status: {e}")
            raise
    
    @staticmethod
    def delete_paper(paper_id):
        """Delete a paper and all associated questions."""
        query = "DELETE FROM papers WHERE id = %s"
        try:
            DatabaseConnection.execute_query(query, (paper_id,))
            logger.info(f"Paper {paper_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting paper: {e}")
            raise
    
    @staticmethod
    def get_paper_count():
        """Get total number of papers."""
        query = "SELECT COUNT(*) as count FROM papers"
        try:
            result = DatabaseConnection.execute_query(query, fetch_one=True)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting paper count: {e}")
            raise
    
    @staticmethod
    def get_unique_subjects():
        """Get list of all unique subjects."""
        query = "SELECT DISTINCT subject FROM papers ORDER BY subject"
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return [row['subject'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting unique subjects: {e}")
            raise
    
    @staticmethod
    def get_unique_years():
        """Get list of all unique years."""
        query = "SELECT DISTINCT year FROM papers WHERE year IS NOT NULL ORDER BY year DESC"
        try:
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return [row['year'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting unique years: {e}")
            raise
