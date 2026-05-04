"""
Session State Management - Streamlit session state utilities.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage Streamlit session state."""
    
    @staticmethod
    def initialize_session():
        """Initialize all required session state variables."""
        
        # User data
        if 'current_subject' not in st.session_state:
            st.session_state.current_subject = None
        
        if 'selected_papers' not in st.session_state:
            st.session_state.selected_papers = []
        
        # Exam/Mock data
        if 'mock_exam' not in st.session_state:
            st.session_state.mock_exam = None
        
        if 'exam_answers' not in st.session_state:
            st.session_state.exam_answers = {}
        
        # UI state
        if 'upload_status' not in st.session_state:
            st.session_state.upload_status = None
        
        if 'analysis_ready' not in st.session_state:
            st.session_state.analysis_ready = False
        
        # Cache data
        if 'cached_analysis' not in st.session_state:
            st.session_state.cached_analysis = {}
        
        if 'cached_questions' not in st.session_state:
            st.session_state.cached_questions = {}
        
        logger.debug("Session initialized")
    
    @staticmethod
    def set_current_subject(subject):
        """Set current subject."""
        st.session_state.current_subject = subject
        st.session_state.analysis_ready = False
        logger.debug(f"Subject set to: {subject}")
    
    @staticmethod
    def get_current_subject():
        """Get current subject."""
        return st.session_state.current_subject
    
    @staticmethod
    def cache_analysis(subject, analysis_data):
        """Cache analysis results."""
        st.session_state.cached_analysis[subject] = analysis_data
        logger.debug(f"Cached analysis for {subject}")
    
    @staticmethod
    def get_cached_analysis(subject):
        """Get cached analysis."""
        return st.session_state.cached_analysis.get(subject)
    
    @staticmethod
    def add_selected_paper(paper_id):
        """Add paper to selection."""
        if paper_id not in st.session_state.selected_papers:
            st.session_state.selected_papers.append(paper_id)
            logger.debug(f"Added paper {paper_id} to selection")
    
    @staticmethod
    def remove_selected_paper(paper_id):
        """Remove paper from selection."""
        if paper_id in st.session_state.selected_papers:
            st.session_state.selected_papers.remove(paper_id)
            logger.debug(f"Removed paper {paper_id} from selection")
    
    @staticmethod
    def get_selected_papers():
        """Get selected papers."""
        return st.session_state.selected_papers
    
    @staticmethod
    def clear_selection():
        """Clear paper selection."""
        st.session_state.selected_papers = []
        logger.debug("Cleared paper selection")
    
    @staticmethod
    def set_mock_exam(exam_data):
        """Set mock exam in session."""
        st.session_state.mock_exam = exam_data
        logger.debug("Mock exam set")
    
    @staticmethod
    def get_mock_exam():
        """Get mock exam from session."""
        return st.session_state.mock_exam
    
    @staticmethod
    def save_exam_answer(question_num, answer):
        """Save exam answer."""
        st.session_state.exam_answers[question_num] = answer
    
    @staticmethod
    def get_exam_answers():
        """Get all exam answers."""
        return st.session_state.exam_answers
    
    @staticmethod
    def clear_exam_answers():
        """Clear all exam answers."""
        st.session_state.exam_answers = {}
        logger.debug("Cleared exam answers")
    
    @staticmethod
    def reset_all():
        """Reset all session state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionManager.initialize_session()
        logger.info("Session reset")


# Initialize on import
SessionManager.initialize_session()
