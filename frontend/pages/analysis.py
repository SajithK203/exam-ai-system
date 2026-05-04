"""
Analysis Dashboard Page - Display exam analytics and patterns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from database.queries.paper_queries import PaperQueries
from database.queries.analytics_queries import AnalyticsQueries
from modules.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)


def show_analysis_page():
    """Display analysis dashboard."""
    
    try:
        # Get unique subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("No papers uploaded yet. Please upload exam papers first.")
            return
        
        # Subject selector
        subject = st.selectbox("Select Subject", options=subjects)
        
        if subject:
            # Get analysis
            with st.spinner(f"Loading analysis for {subject}..."):
                analysis = AnalyticsEngine.get_full_analysis(subject)
            
            # Topic Frequency Chart
            st.subheader("📊 Topic Frequency Distribution")
            
            topic_freq = analysis.get('topic_frequency', [])
            if topic_freq:
                df_topics = pd.DataFrame(topic_freq).head(10)
                
                fig = px.bar(
                    df_topics,
                    x='topic_name',
                    y='frequency',
                    title=f"Most Asked Topics in {subject}",
                    labels={'frequency': 'Number of Questions', 'topic_name': 'Topic'},
                    color='frequency',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No topic frequency data available")
            
            # Question Type Distribution
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
                        title="Distribution by Type"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No question type data")
            
            with col2:
                st.subheader("📈 Difficulty Distribution")
                difficulty = analysis.get('difficulty_distribution', [])
                
                if difficulty:
                    df_diff = pd.DataFrame(difficulty)
                    
                    fig = px.pie(
                        df_diff,
                        values='count',
                        names='difficulty_level',
                        title="Distribution by Difficulty"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No difficulty data")
            
            # Papers Per Year Trend
            st.subheader("📅 Papers Per Year Trend")
            papers_per_year = analysis.get('papers_per_year', [])
            
            if papers_per_year:
                df_years = pd.DataFrame(papers_per_year).sort_values('year')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_years['year'],
                    y=df_years['paper_count'],
                    mode='lines+markers',
                    name='Papers',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Number of Papers Per Year",
                    xaxis_title="Year",
                    yaxis_title="Number of Papers",
                    height=300,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Statistics Summary
            st.subheader("📈 Statistics Summary")
            
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            
            with stats_col1:
                papers = PaperQueries.get_papers_by_subject(subject)
                st.metric("Total Papers", len(papers))
            
            with stats_col2:
                st.metric("Unique Topics", len(analysis.get('topic_frequency', [])))
            
            with stats_col3:
                years = PaperQueries.get_unique_years()
                st.metric("Years Covered", len([y for y in years if True]))
            
            with stats_col4:
                st.metric("Question Types", len(analysis.get('question_type_distribution', [])))
            
            # Trending Topics
            st.subheader("🔥 Trending Topics (Last 5 Years)")
            
            trends = analysis.get('topic_trends', [])
            if trends:
                df_trends = pd.DataFrame(trends)
                
                # Create pivot table for better visualization
                if 'year' in df_trends.columns and 'topic_name' in df_trends.columns:
                    pivot_df = df_trends.pivot_table(
                        values='frequency',
                        index='topic_name',
                        columns='year',
                        fill_value=0
                    )
                    
                    st.dataframe(pivot_df, use_container_width=True)
            
            else:
                st.info("No trend data available")
    
    except Exception as e:
        st.error(f"Error loading analysis: {e}")
        logger.error(f"Analysis page error: {e}")
