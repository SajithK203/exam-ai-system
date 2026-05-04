"""
Questions Page - Display and search extracted questions.
"""

import streamlit as st
import pandas as pd
import logging
from database.queries.paper_queries import PaperQueries
from database.queries.question_queries import QuestionQueries
from database.queries.analytics_queries import AnalyticsQueries

logger = logging.getLogger(__name__)


def show_questions_page():
    """Display questions bank."""
    
    try:
        # Get subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("No questions available yet. Upload exam papers first.")
            return
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 By Subject", "🔍 Search", "🔁 Repeated Questions"])
        
        with tab1:
            st.subheader("Questions by Subject")
            
            subject = st.selectbox("Select Subject", options=subjects, key="subject_select")
            
            if subject:
                # Get questions
                questions = QuestionQueries.get_questions_by_subject(subject)
                
                if questions:
                    # Filter options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        question_type = st.selectbox(
                            "Filter by Type",
                            options=["All"] + list(set([q.get('question_type', 'Unknown') for q in questions])),
                            key="type_filter"
                        )
                    
                    with col2:
                        year = st.selectbox(
                            "Filter by Year",
                            options=["All"] + sorted(set([str(q.get('year', 'Unknown')) for q in questions]), reverse=True),
                            key="year_filter"
                        )
                    
                    with col3:
                        topic = st.selectbox(
                            "Filter by Topic",
                            options=["All"] + sorted(set([q.get('topic_name', 'Unclassified') for q in questions if q.get('topic_name')])),
                            key="topic_filter"
                        )
                    
                    # Apply filters
                    filtered = questions
                    
                    if question_type != "All":
                        filtered = [q for q in filtered if q.get('question_type') == question_type]
                    
                    if year != "All":
                        filtered = [q for q in filtered if str(q.get('year')) == year]
                    
                    if topic != "All":
                        filtered = [q for q in filtered if q.get('topic_name') == topic]
                    
                    # Display questions
                    st.write(f"**Found {len(filtered)} questions**")
                    
                    for i, q in enumerate(filtered, 1):
                        with st.expander(f"Q{i}: {q.get('question_text', 'N/A')[:80]}..."):
                            st.write(f"**Full Question:** {q.get('question_text', 'N/A')}")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.write(f"**Type:** {q.get('question_type', 'Unknown')}")
                            with col2:
                                st.write(f"**Topic:** {q.get('topic_name', 'Unclassified')}")
                            with col3:
                                st.write(f"**Year:** {q.get('year', 'N/A')}")
                            with col4:
                                st.write(f"**Marks:** {q.get('marks_allocated', 0)}")
                
                else:
                    st.info("No questions found for this subject")
        
        with tab2:
            st.subheader("Search Questions")
            
            search_text = st.text_input("Enter search terms", placeholder="e.g., binary tree, algorithm")
            
            if search_text:
                try:
                    results = QuestionQueries.search_questions(search_text)
                    
                    if results:
                        st.write(f"**Found {len(results)} matching questions**")
                        
                        for i, q in enumerate(results, 1):
                            with st.expander(f"Match {i}: {q.get('question_text', 'N/A')[:80]}..."):
                                st.write(f"**Question:** {q.get('question_text', 'N/A')}")
                                st.write(f"**Topic:** {q.get('topic_name', 'N/A')}")
                                st.write(f"**Year:** {q.get('year', 'N/A')}")
                                st.write(f"**Subject:** {q.get('subject', 'N/A')}")
                    else:
                        st.info("No matching questions found")
                
                except Exception as e:
                    st.warning(f"Search error: {e}")
        
        with tab3:
            st.subheader("Repeated Questions")
            
            if st.button("🔍 Find Repeated Questions"):
                with st.spinner("Searching..."):
                    try:
                        repeated = AnalyticsQueries.get_repeated_questions()
                        
                        if repeated:
                            st.write(f"**Found {len(repeated)} repeated questions**")
                            
                            for i, item in enumerate(repeated[:10], 1):
                                with st.expander(f"Q{i} (appeared {item.get('paper_count', 0)} times): {item.get('question_text', 'N/A')[:80]}..."):
                                    st.write(f"**Question:** {item.get('question_text', 'N/A')}")
                                    st.write(f"**Topic:** {item.get('topic_name', 'N/A')}")
                                    st.write(f"**Times Appeared:** {item.get('paper_count', 0)}")
                                    st.write(f"**Total Occurrences:** {item.get('total_occurrences', 0)}")
                        else:
                            st.info("No repeated questions found")
                    
                    except Exception as e:
                        st.error(f"Error finding repeated questions: {e}")
    
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        logger.error(f"Questions page error: {e}")
