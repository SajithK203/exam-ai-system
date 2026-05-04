"""
Insights Page - Display AI recommendations and insights.
"""

import streamlit as st
import logging
from database.queries.paper_queries import PaperQueries
from ai.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


def show_insights_page():
    """Display AI insights and recommendations."""
    
    try:
        # Get subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("No data available. Please upload exam papers first.")
            return
        
        # Subject selector
        subject = st.selectbox("Select Subject", options=subjects, key="insights_subject")
        
        if subject:
            # Insight type selector
            insight_type = st.radio(
                "Choose Insight Type",
                options=[
                    "📚 Study Plan",
                    "📝 Mock Exam Suggestions",
                    "⚠️ Weak Areas",
                    "⏱️ Time Management"
                ],
                horizontal=True
            )
            
            if st.button("🚀 Generate Insights", type="primary"):
                with st.spinner("Generating AI insights..."):
                    try:
                        if insight_type == "📚 Study Plan":
                            result = RecommendationEngine.generate_study_plan(subject)
                            
                            st.subheader("📚 AI-Generated Study Plan")
                            st.write(result['ai_recommendation'])
                            
                            st.subheader("📌 Top Topics to Focus On")
                            for i, topic in enumerate(result['top_topics'], 1):
                                st.write(f"{i}. **{topic['topic_name']}** ({topic['frequency']} questions)")
                        
                        elif insight_type == "📝 Mock Exam Suggestions":
                            result = RecommendationEngine.generate_mock_exam_suggestions(subject)
                            
                            st.subheader("📝 Mock Exam Generation Suggestions")
                            st.write(result['suggestions'])
                            
                            st.subheader("📌 Recommended Topics")
                            for topic in result['recommended_topics']:
                                st.write(f"- {topic['topic_name']} ({topic['frequency']} questions)")
                        
                        elif insight_type == "⚠️ Weak Areas":
                            result = RecommendationEngine.generate_weak_area_analysis(subject)
                            
                            st.subheader("⚠️ Weak Areas Analysis")
                            st.write(result['analysis'])
                        
                        elif insight_type == "⏱️ Time Management":
                            result = RecommendationEngine.generate_time_management_plan(subject)
                            
                            st.subheader("⏱️ Time Management Strategy")
                            st.write(result['strategy'])
                            
                            stats = result['exam_stats']
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Papers", stats['total_papers'])
                            with col2:
                                st.metric("Total Questions", stats['total_questions'])
                            with col3:
                                st.metric("Avg Per Paper", f"{stats['avg_questions_per_paper']:.1f}")
                    
                    except Exception as e:
                        st.error(f"Error generating insights: {e}")
                        logger.error(f"Insight generation error: {e}")
            
            st.divider()
            
            # Additional info
            with st.expander("ℹ️ About These Insights"):
                st.markdown("""
                These AI-powered insights are generated based on:
                
                - **Historical Exam Patterns**: Analysis of past papers
                - **Topic Frequency**: Most frequently asked topics
                - **Difficulty Distribution**: Mix of easy, medium, hard questions
                - **Question Types**: Distribution of MCQ, short answer, long answer
                - **Temporal Trends**: Changes in topics over years
                
                These insights are designed to help you:
                - Focus your study on high-value topics
                - Manage your exam time effectively
                - Identify weak areas for improvement
                - Create effective mock exams
                """)
    
    except Exception as e:
        st.error(f"Error loading insights: {e}")
        logger.error(f"Insights page error: {e}")
