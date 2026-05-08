"""
Analysis Dashboard Page - Display exam analytics and patterns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
from database.queries.paper_queries import PaperQueries
from database.queries.analytics_queries import AnalyticsQueries
from database.queries.question_queries import QuestionQueries
from modules.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)


def show_analysis_page():
    """Display analysis dashboard with real-time updates."""
    
    try:
        # Auto-refresh mechanism
        st.session_state.page_refresh = st.session_state.get('page_refresh', 0)
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 Refresh", help="Refresh all data"):
                st.session_state.page_refresh += 1
                st.rerun()
        
        # Get unique subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("📭 No papers uploaded yet. Please upload exam papers first.")
            return
        
        # Subject selector
        selected_subject = st.selectbox(
            "📚 Select Subject",
            options=subjects,
            key="subject_selector"
        )
        
        if not selected_subject:
            return
        
        # Load analysis data
        with st.spinner(f"Loading analysis for {selected_subject}..."):
            try:
                analysis = AnalyticsEngine.get_full_analysis(selected_subject)
                
                # Get total stats
                papers = PaperQueries.get_papers_by_subject(selected_subject)
                total_papers = len(papers) if papers else 0
                total_questions = sum([p.get('total_questions', 0) for p in papers])
                
            except Exception as e:
                logger.error(f"Error loading analysis: {e}")
                st.error(f"Error loading analysis: {e}")
                return
        
        # Summary Statistics Section
        st.subheader("📈 Statistics Summary")
        
        # Calculate additional stats
        topic_freq = analysis.get('topic_frequency', [])
        unique_topics = len(topic_freq)
        
        question_types = analysis.get('question_type_distribution', [])
        unique_question_types = len(question_types)
        
        years = PaperQueries.get_unique_years() or []
        years_covered = len(years)
        
        # Create metrics row
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
        
        with metric_col1:
            st.metric("📄 Total Papers", total_papers)
        with metric_col2:
            st.metric("❓ Total Questions", total_questions)
        with metric_col3:
            st.metric("🏷️ Unique Topics", unique_topics)
        with metric_col4:
            st.metric("📝 Question Types", unique_question_types)
        with metric_col5:
            st.metric("📅 Years Covered", years_covered)
        
        st.markdown("---")
        
        # Topic Frequency Chart
        st.subheader("📊 Topic Frequency Distribution")
        
        if topic_freq:
            df_topics = pd.DataFrame(topic_freq)
            
            # Handle NULL topic names
            df_topics['topic_name'] = df_topics['topic_name'].fillna('Unclassified')
            df_topics = df_topics.sort_values('frequency', ascending=False).head(10)
            
            fig = px.bar(
                df_topics,
                x='topic_name',
                y='frequency',
                title=f"Top 10 Most Asked Topics in {selected_subject}",
                labels={'frequency': 'Number of Questions', 'topic_name': 'Topic'},
                color='frequency',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                showlegend=False
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📭 No topic frequency data available")
        
        # Question Type and Difficulty Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("❓ Question Type Distribution")
            question_types = analysis.get('question_type_distribution', [])
            
            if question_types:
                df_types = pd.DataFrame(question_types)
                
                fig = px.pie(
                    df_types,
                    values='count',
                    names='question_type',
                    title="Distribution by Type",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("📭 No question type data")
        
        with col2:
            st.subheader("📈 Difficulty Distribution")
            difficulty = analysis.get('difficulty_distribution', [])
            
            if difficulty:
                df_diff = pd.DataFrame(difficulty)
                
                # Order difficulty levels
                difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
                df_diff['sort_key'] = df_diff['difficulty_level'].map(difficulty_order)
                df_diff = df_diff.sort_values('sort_key')
                
                fig = px.bar(
                    df_diff,
                    x='difficulty_level',
                    y='count',
                    title="Distribution by Difficulty",
                    color='difficulty_level',
                    color_discrete_map={'Easy': '#90EE90', 'Medium': '#FFD700', 'Hard': '#FF6B6B'},
                    labels={'count': 'Number of Questions', 'difficulty_level': 'Difficulty'}
                )
                
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("📭 No difficulty data")
        
        # Papers Per Year Trend
        st.subheader("📅 Papers Per Year Trend")
        papers_per_year = analysis.get('papers_per_year', [])
        
        if papers_per_year:
            df_year = pd.DataFrame(papers_per_year)
            
            fig = px.line(
                df_year,
                x='year',
                y='paper_count',
                markers=True,
                title=f"Paper Uploads Over Time for {selected_subject}",
                labels={'paper_count': 'Number of Papers', 'year': 'Year'}
            )
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📭 No year trend data")
        
        # Trending Topics
        st.subheader("🔥 Trending Topics (Last 5 Years)")
        trending_topics = analysis.get('topic_trends', [])
        
        if trending_topics:
            df_trend = pd.DataFrame(trending_topics)
            
            fig = px.scatter(
                df_trend,
                x='year',
                y='frequency',
                size='frequency',
                color='topic_name',
                hover_name='topic_name',
                title=f"Topic Trends in {selected_subject}",
                labels={'frequency': 'Number of Questions', 'year': 'Year'},
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📭 No trend data available")
        
        # Top Topics to Focus On
        st.subheader("🎯 Recommended Focus Areas")
        top_topics = analysis.get('top_topics', [])
        
        if top_topics:
            focus_df = pd.DataFrame(top_topics[:5])
            focus_df.index = focus_df.index + 1
            # Ensure frequency is int for proper display
            focus_df['frequency'] = focus_df['frequency'].astype(int)
            
            st.dataframe(
                focus_df,
                use_container_width=True
            )
        else:
            st.info("📭 No focus areas recommended yet")
        
        # Detailed Statistics
        st.subheader("📋 Detailed Statistics")
        
        with st.expander("View Detailed Tables"):
            tab1, tab2, tab3 = st.tabs(["Topics", "Question Types", "Difficulty"])
            
            with tab1:
                if topic_freq:
                    df_topics_detail = pd.DataFrame(topic_freq)
                    df_topics_detail['topic_name'] = df_topics_detail['topic_name'].fillna('Unclassified')
                    st.dataframe(df_topics_detail, width='stretch')
                else:
                    st.info("No topic data")
            
            with tab2:
                if question_types:
                    st.dataframe(pd.DataFrame(question_types), width='stretch')
                else:
                    st.info("No question type data")
            
            with tab3:
                if difficulty:
                    st.dataframe(pd.DataFrame(difficulty), width='stretch')
                else:
                    st.info("No difficulty data")
        
        # Add timestamp
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Error in analysis page: {e}")
        st.error(f"Error loading analysis dashboard: {e}")
