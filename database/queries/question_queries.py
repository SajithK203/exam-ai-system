"""
Question query operations - CRUD operations for exam questions.
Includes pagination, update, MCQ option storage, and confidence tracking.
"""

from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class QuestionQueries:
    """Handle all question-related database operations."""

    @staticmethod
    def create_question(paper_id, question_text, topic_id, question_type,
                        marks=0, difficulty='Medium',
                        ai_classified=False, topic_confidence=0.0):
        """Create a new question record."""
        query = """
            INSERT INTO questions
            (paper_id, question_text, topic_id, question_type, marks_allocated,
             difficulty_level, ai_classified, topic_confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (paper_id, question_text, topic_id, question_type, marks,
                  difficulty, ai_classified, topic_confidence)
        try:
            DatabaseConnection.execute_query(query, params)
            # Return the last insert ID
            id_result = DatabaseConnection.execute_query(
                "SELECT LAST_INSERT_ID() as id", fetch_one=True
            )
            return id_result['id'] if id_result else None
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            raise

    @staticmethod
    def save_question_options(question_id, options):
        """
        Save MCQ options for a question.

        Args:
            question_id: ID of the question
            options: List of dicts [{'label': 'A', 'text': '...'}]
        """
        if not options:
            return
        try:
            # Clear existing options first (idempotent)
            DatabaseConnection.execute_query(
                "DELETE FROM question_options WHERE question_id = %s", (question_id,)
            )
            insert_query = """
                INSERT INTO question_options (question_id, option_text, option_label)
                VALUES (%s, %s, %s)
            """
            for opt in options:
                DatabaseConnection.execute_query(
                    insert_query,
                    (question_id, opt.get('text', ''), opt.get('label', ''))
                )
            logger.info(f"Saved {len(options)} options for question {question_id}")
        except Exception as e:
            logger.error(f"Error saving question options: {e}")
            # Non-fatal — don't raise, question was already saved

    @staticmethod
    def get_question_options(question_id):
        """Fetch MCQ options for a question."""
        query = """
            SELECT option_label, option_text, is_correct
            FROM question_options
            WHERE question_id = %s
            ORDER BY option_label
        """
        try:
            result = DatabaseConnection.execute_query(query, (question_id,), fetch_all=True)
            return result if result else []
        except Exception as e:
            logger.error(f"Error fetching question options: {e}")
            return []

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
    def get_questions_by_subject(subject):
        """Get all questions for a subject (no pagination — use paged version for large sets)."""
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
    def get_questions_by_subject_paged(subject, page=1, page_size=20,
                                        filter_type=None, filter_year=None, filter_topic=None):
        """
        Get paginated questions for a subject with optional filters.

        Returns:
            (questions_list, total_count)
        """
        # Build WHERE clause dynamically
        conditions = ["p.subject = %s"]
        params = [subject]

        if filter_type and filter_type != "All":
            conditions.append("q.question_type = %s")
            params.append(filter_type)
        if filter_year and filter_year != "All":
            conditions.append("p.year = %s")
            params.append(int(filter_year))
        if filter_topic and filter_topic != "All":
            conditions.append("t.topic_name = %s")
            params.append(filter_topic)

        where_clause = " AND ".join(conditions)
        offset = (page - 1) * page_size

        # Count query
        count_query = f"""
            SELECT COUNT(q.id) as total
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE {where_clause}
        """
        # Data query
        data_query = f"""
            SELECT q.*, p.year, t.topic_name
            FROM questions q
            JOIN papers p ON q.paper_id = p.id
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE {where_clause}
            ORDER BY p.year DESC, q.id ASC
            LIMIT %s OFFSET %s
        """

        try:
            count_result = DatabaseConnection.execute_query(count_query, params, fetch_one=True)
            total = count_result['total'] if count_result else 0

            data_result = DatabaseConnection.execute_query(
                data_query, params + [page_size, offset], fetch_all=True
            )
            return data_result or [], total
        except Exception as e:
            logger.error(f"Error fetching paged questions: {e}")
            return [], 0

    @staticmethod
    def update_question(question_id, topic_id=None, question_type=None,
                        marks_allocated=None, difficulty_level=None,
                        question_text=None):
        """
        Update one or more fields of a question.

        Only provided (non-None) fields are updated.
        """
        fields = []
        params = []

        if question_text is not None:
            fields.append("question_text = %s")
            params.append(question_text)
        if topic_id is not None:
            fields.append("topic_id = %s")
            params.append(topic_id)
        if question_type is not None:
            fields.append("question_type = %s")
            params.append(question_type)
        if marks_allocated is not None:
            fields.append("marks_allocated = %s")
            params.append(marks_allocated)
        if difficulty_level is not None:
            fields.append("difficulty_level = %s")
            params.append(difficulty_level)

        if not fields:
            return True  # Nothing to update

        query = f"UPDATE questions SET {', '.join(fields)} WHERE id = %s"
        params.append(question_id)

        try:
            DatabaseConnection.execute_query(query, params)
            logger.info(f"Question {question_id} updated: {fields}")
            return True
        except Exception as e:
            logger.error(f"Error updating question: {e}")
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
        return QuestionQueries.update_question(question_id, topic_id=topic_id)

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
    def get_repeated_questions(page=1, page_size=20):
        """
        Get questions that appeared multiple times across papers, with pagination.

        Returns:
            (repeated_list, total_count)
        """
        offset = (page - 1) * page_size

        count_query = """
            SELECT COUNT(*) as total FROM (
                SELECT COUNT(DISTINCT q.paper_id) as paper_count
                FROM questions q
                JOIN papers p ON q.paper_id = p.id
                GROUP BY LOWER(q.question_text), q.topic_id, q.question_type, p.subject
                HAVING paper_count > 1
            ) sub
        """

        data_query = """
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
            LIMIT %s OFFSET %s
        """
        try:
            count_result = DatabaseConnection.execute_query(count_query, fetch_one=True)
            total = count_result['total'] if count_result else 0
            data_result = DatabaseConnection.execute_query(data_query, (page_size, offset), fetch_all=True)
            return data_result or [], total
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
