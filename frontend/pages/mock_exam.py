"""
Mock Exam Page - Generate and manage mock exams.
"""

import streamlit as st
import logging
import random
from database.queries.paper_queries import PaperQueries
from database.queries.question_queries import QuestionQueries
from database.queries.analytics_queries import AnalyticsQueries
from modules.topic_classifier import TopicClassifier

logger = logging.getLogger(__name__)


def show_mock_exam_page():
    """Display mock exam generator."""
    
    try:
        # Get subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("No questions available. Please upload exam papers first.")
            return
        
        # Configuration section
        st.subheader("⚙️ Configure Mock Exam")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject = st.selectbox("Select Subject", options=subjects, key="mock_subject")
        
        with col2:
            num_questions = st.slider("Number of Questions", min_value=5, max_value=50, value=10)
        
        with col3:
            total_marks = st.number_input("Total Marks", min_value=10, max_value=500, value=100)
        
        # Question distribution
        st.subheader("📊 Question Distribution")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mcq_percent = st.slider("% Multiple Choice", 0, 100, 30)
        
        with col2:
            short_ans_percent = st.slider("% Short Answer", 0, 100, 40)
        
        with col3:
            long_ans_percent = 100 - mcq_percent - short_ans_percent
            st.write(f"**% Long Answer: {long_ans_percent}%**")
        
        # Difficulty level
        st.subheader("📈 Difficulty Distribution")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            easy_percent = st.slider("% Easy", 0, 100, 20)
        
        with col2:
            medium_percent = st.slider("% Medium", 0, 100, 50)
        
        with col3:
            hard_percent = 100 - easy_percent - medium_percent
            st.write(f"**% Hard: {hard_percent}%**")
        
        # Generate button
        if st.button("🎯 Generate Mock Exam", type="primary"):
            with st.spinner("Generating mock exam..."):
                try:
                    # Get all questions for subject
                    all_questions = QuestionQueries.get_questions_by_subject(subject)
                    
                    if not all_questions:
                        st.error("No questions found for this subject")
                        return
                    
                    # Calculate number of each type
                    num_mcq = max(1, int(num_questions * mcq_percent / 100))
                    num_short = max(1, int(num_questions * short_ans_percent / 100))
                    num_long = num_questions - num_mcq - num_short
                    
                    # Calculate number of each difficulty
                    num_easy = max(0, int(num_questions * easy_percent / 100))
                    num_medium = max(1, int(num_questions * medium_percent / 100))
                    num_hard = num_questions - num_easy - num_medium
                    
                    # Filter questions by type
                    mcq_questions = [q for q in all_questions if q.get('question_type') == 'Multiple Choice']
                    short_questions = [q for q in all_questions if q.get('question_type') == 'Short Answer']
                    long_questions = [q for q in all_questions if q.get('question_type') == 'Long Answer']
                    
                    # Select questions
                    selected = []
                    
                    if mcq_questions:
                        selected.extend(random.sample(mcq_questions, min(num_mcq, len(mcq_questions))))
                    
                    if short_questions:
                        selected.extend(random.sample(short_questions, min(num_short, len(short_questions))))
                    
                    if long_questions:
                        selected.extend(random.sample(long_questions, min(num_long, len(long_questions))))
                    
                    # If not enough selected, fill with any available
                    remaining = num_questions - len(selected)
                    if remaining > 0:
                        available = [q for q in all_questions if q not in selected]
                        selected.extend(random.sample(available, min(remaining, len(available))))
                    
                    # Shuffle
                    random.shuffle(selected)
                    
                    # Store in session
                    st.session_state.mock_exam = {
                        'subject': subject,
                        'questions': selected,
                        'total_marks': total_marks,
                        'answers': {}
                    }
                    
                    st.success("✅ Mock exam generated!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating mock exam: {e}")
                    logger.error(f"Mock exam generation error: {e}")
        
        # Display mock exam if generated
        if 'mock_exam' in st.session_state and st.session_state.mock_exam:
            exam = st.session_state.mock_exam
            
            st.divider()
            st.subheader("📝 Mock Exam")
            st.write(f"**Subject:** {exam['subject']}")
            st.write(f"**Total Questions:** {len(exam['questions'])}")
            st.write(f"**Total Marks:** {exam['total_marks']}")
            
            st.divider()
            
            # Display questions
            for i, q in enumerate(exam['questions'], 1):
                with st.expander(f"Q{i}: {q.get('question_text', 'N/A')[:80]}... ({q.get('question_type', 'N/A')})"):
                    st.write(f"**Question:** {q.get('question_text', 'N/A')}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Type:** {q.get('question_type', 'N/A')}")
                    with col2:
                        st.write(f"**Topic:** {q.get('topic_name', 'Unclassified')}")
                    with col3:
                        st.write(f"**Marks:** {q.get('marks_allocated', 0)}")
                    
                    st.divider()
                    
                    # Answer field
                    answer = st.text_area(
                        f"Your Answer (Q{i}):",
                        value=exam['answers'].get(i, ''),
                        height=100,
                        key=f"answer_{i}"
                    )
                    
                    exam['answers'][i] = answer
            
            st.divider()
            
            # Submit button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Save Answers"):
                    st.success("✅ Answers saved!")
            
            with col2:
                if st.button("🔄 Generate New Exam"):
                    st.session_state.mock_exam = None
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading mock exam: {e}")
        logger.error(f"Mock exam page error: {e}")
