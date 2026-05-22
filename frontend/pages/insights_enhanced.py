"""
Enhanced Insights Page - Evidence-based exam intelligence system.
Shows analytics-backed insights with data citations and confidence levels.
"""

import streamlit as st
import logging
import pandas as pd
from database.queries.paper_queries import PaperQueries
from ai.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


def show_confidence_badge(confidence_level):
    """Display confidence level badge."""
    if confidence_level == 'High':
        return "🟢 High Confidence"
    elif confidence_level == 'Medium':
        return "🟡 Medium Confidence"
    else:
        return "🔴 Low Confidence"


def display_topic_with_evidence(topic_data):
    """Display a topic with evidence citations."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write(f"**{topic_data['topic_name']}**")
    with col2:
        if 'intelligence_score' in topic_data:
            st.metric("Score", f"{topic_data['intelligence_score']:.0f}/100")
    with col3:
        st.metric("Frequency", f"{topic_data['frequency']}×")
    
    # Evidence details
    with st.expander("📊 Evidence"):
        st.markdown(f"""
- **Appeared {topic_data['frequency']} times** in exams
- **Confidence**: {topic_data.get('confidence', 'Medium')}
- **Based on**: {len(PaperQueries.get_papers_by_subject(topic_data.get('subject', ''))) if 'subject' in topic_data else '?'} past papers analyzed
        """)


def show_insights_page():
    """Display enhanced AI insights and recommendations with evidence."""
    
    try:
        # Get subjects
        subjects = PaperQueries.get_unique_subjects()
        
        if not subjects:
            st.warning("No data available. Please upload exam papers first.")
            return
        
        # Subject selector
        subject = st.selectbox("Select Subject", options=subjects, key="insights_subject")
        
        if subject:
            # Improved navigation with tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📚 Study Strategy",
                "📈 Topic Trends",
                "⚠️ Risk Areas",
                "⏱️ Time Strategy",
                "🎯 Predicted Focus"
            ])
            
            # ============= TAB 1: STUDY STRATEGY =============
            with tab1:
                st.subheader("📚 AI-Generated Study Strategy")
                st.write("Based on comprehensive exam analysis with evidence.")
                
                if st.button("🚀 Generate Study Plan", type="primary", key="study_plan_btn"):
                    with st.spinner("Analyzing exam patterns..."):
                        try:
                            result = RecommendationEngine.generate_study_plan(subject)
                            
                            # Display confidence
                            st.info(f"**{show_confidence_badge(result.get('confidence', 'Medium'))}** "
                                   f"- Based on analysis of exam data")
                            
                            # Display top topics with intelligence scores
                            st.subheader("🏆 Top Priority Topics")
                            
                            # Create dataframe for better visualization
                            if result.get('topic_intelligence_scores'):
                                df = pd.DataFrame(result['topic_intelligence_scores'][:5])
                                df = df[['topic_name', 'frequency', 'intelligence_score', 'confidence']]
                                df.columns = ['Topic', 'Times Asked', 'Intelligence Score', 'Confidence']
                                
                                st.dataframe(df, use_container_width=True)
                            
                            # Display recommendations
                            st.subheader("💡 AI Recommendations")
                            st.markdown(result['ai_recommendation'])
                            
                            # Medium priority topics
                            if result.get('medium_priority'):
                                st.subheader("📌 Secondary Focus Topics")
                                for topic in result['medium_priority']:
                                    display_topic_with_evidence(topic)
                        
                        except Exception as e:
                            st.error(f"Error generating study plan: {e}")
                            logger.error(f"Study plan error: {e}")
            
            # ============= TAB 2: TOPIC TRENDS =============
            with tab2:
                st.subheader("📈 Topic Popularity Trends")
                st.write("Shows how topics have changed over recent years.")
                
                if st.button("📊 Analyze Trends", type="primary", key="trends_btn"):
                    with st.spinner("Analyzing topic trends..."):
                        try:
                            from database.queries.analytics_queries import AnalyticsQueries
                            
                            trending_topics = AnalyticsQueries.get_trending_topics(subject, years=5)
                            
                            if trending_topics:
                                # Group by year for visualization
                                years_data = {}
                                for trend in trending_topics:
                                    year = trend.get('year')
                                    topic = trend.get('topic_name')
                                    freq = trend.get('frequency', 0)
                                    
                                    if year not in years_data:
                                        years_data[year] = {}
                                    years_data[year][topic] = freq
                                
                                # Display trend insights
                                st.info("""
                                **Trend Analysis**: Topics with increasing frequency are becoming more important.
                                Focus on topics with upward trends for better exam preparation.
                                """)
                                
                                # Show year-by-year breakdown
                                for year in sorted(years_data.keys(), reverse=True):
                                    st.write(f"**{year}**: {', '.join([f'{t} ({f}×)' for t, f in sorted(years_data[year].items(), key=lambda x: x[1], reverse=True)[:5]])}")
                        
                        except Exception as e:
                            st.error(f"Error analyzing trends: {e}")
                            logger.error(f"Trends error: {e}")
            
            # ============= TAB 3: WEAK AREAS =============
            with tab3:
                st.subheader("⚠️ Risk Areas Analysis")
                st.write("Topics that are frequently asked AND difficult - high-priority study areas.")
                
                if st.button("🔍 Identify Risk Areas", type="primary", key="weak_areas_btn"):
                    with st.spinner("Analyzing risk patterns..."):
                        try:
                            result = RecommendationEngine.generate_weak_area_analysis(subject)
                            
                            # Display confidence
                            st.info(f"**{show_confidence_badge(result.get('confidence', 'Medium'))}**")
                            
                            # Display weak areas with evidence
                            st.subheader("High-Priority Risk Areas (Scored by Importance)")
                            
                            if result.get('weak_areas_ranked'):
                                for i, area in enumerate(result['weak_areas_ranked'][:5], 1):
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.write(f"**{i}. {area['topic']}**")
                                    with col2:
                                        st.metric("Asked", f"{area['frequency']}×")
                                    with col3:
                                        st.metric("Years", area['years_appeared'])
                                    with col4:
                                        st.metric("Difficulty", f"{area['difficulty_level']:.1f}/3")
                            
                            # Display analysis
                            st.subheader("📋 Detailed Analysis")
                            st.markdown(result['analysis'])
                        
                        except Exception as e:
                            st.error(f"Error analyzing weak areas: {e}")
                            logger.error(f"Weak areas error: {e}")
            
            # ============= TAB 4: TIME STRATEGY =============
            with tab4:
                st.subheader("⏱️ Time Management Strategy")
                st.write("Evidence-based time allocation for exam preparation.")
                
                if st.button("⏰ Generate Time Strategy", type="primary", key="time_strategy_btn"):
                    with st.spinner("Calculating optimal time allocation..."):
                        try:
                            result = RecommendationEngine.generate_time_management_plan(subject)
                            
                            # Display confidence
                            st.info(f"**{show_confidence_badge(result.get('confidence', 'Medium'))}**")
                            
                            # Display exam statistics
                            stats = result['exam_stats']
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Papers", stats['total_papers'])
                            with col2:
                                st.metric("Total Questions", stats['total_questions'])
                            with col3:
                                st.metric("Avg Per Paper", f"{stats['avg_questions_per_paper']:.1f}")
                            with col4:
                                st.metric("Years Covered", stats['years_covered'])
                            
                            # Display strategy
                            st.subheader("📌 Time Allocation Strategy")
                            st.markdown(result['strategy'])
                            
                            # Show question distribution
                            if result.get('question_distribution'):
                                st.subheader("Question Type Distribution")
                                df_types = pd.DataFrame(result['question_distribution'])
                                st.dataframe(df_types[['question_type', 'count', 'percentage']], use_container_width=True)
                            
                            # Show difficulty distribution
                            if result.get('difficulty_distribution'):
                                st.subheader("Difficulty Distribution")
                                df_diff = pd.DataFrame(result['difficulty_distribution'])
                                st.dataframe(df_diff, use_container_width=True)
                        
                        except Exception as e:
                            st.error(f"Error generating time strategy: {e}")
                            logger.error(f"Time strategy error: {e}")
            
            # ============= TAB 5: PREDICTED IMPORTANT AREAS =============
            with tab5:
                st.subheader("🎯 Predicted Important Focus Areas")
                st.write("Topics most likely to appear in upcoming exams based on historical patterns.")
                
                if st.button("🔮 Predict Focus Areas", type="primary", key="predict_btn"):
                    with st.spinner("Analyzing patterns for predictions..."):
                        try:
                            from database.queries.analytics_queries import AnalyticsQueries
                            
                            # Get top topics with trend data
                            top_topics = AnalyticsQueries.get_top_topics(subject, limit=15)
                            trending = AnalyticsQueries.get_trending_topics(subject, years=3)
                            
                            st.info("""
                            **Prediction Logic**: Based on frequency + recent trends + difficulty
                            """)
                            
                            predictions = []
                            for topic in top_topics[:10]:
                                # Check if trending up
                                trend_score = 0
                                for t in trending:
                                    if t.get('topic_name') == topic['topic_name']:
                                        trend_score = t.get('frequency', 0)
                                
                                prediction_score = (topic['frequency'] * 6) + (trend_score * 4)
                                
                                predictions.append({
                                    'Topic': topic['topic_name'],
                                    'Frequency': topic['frequency'],
                                    'Recent Trend': '📈 Up' if trend_score > 0 else '📉 Stable',
                                    'Prediction Score': min(100, prediction_score)
                                })
                            
                            # Sort by prediction score
                            predictions.sort(key=lambda x: x['Prediction Score'], reverse=True)
                            
                            df_pred = pd.DataFrame(predictions)
                            st.dataframe(df_pred, use_container_width=True)
                            
                            st.success("✅ Focus on these topics for maximum exam impact!")
                        
                        except Exception as e:
                            st.error(f"Error predicting focus areas: {e}")
                            logger.error(f"Prediction error: {e}")
            
            # ============= ABOUT SECTION =============
            st.divider()
            with st.expander("ℹ️ About These Evidence-Based Insights"):
                st.markdown("""
                ## Why Evidence-Based Insights?
                
                Instead of generic AI advice, these insights are grounded in real exam data:
                
                ### What Makes Them Reliable
                - **Historical Exam Patterns**: Analysis of past papers
                - **Topic Frequency**: How many times topics actually appear
                - **Temporal Analysis**: Which years and trends matter
                - **Difficulty Data**: Real question difficulty distribution
                - **Question Types**: What type of questions dominate
                
                ### Key Features
                
                1. **Topic Intelligence Score** 🏆
                   - Combines: frequency + recent trends + difficulty
                   - Scores out of 100 for prioritization
                
                2. **Confidence Levels** 🎯
                   - High: Based on 5+ years of data
                   - Medium: Based on 2-5 years of data
                   - Low: Based on limited data
                
                3. **Risk Area Scoring** ⚠️
                   - Identifies high-frequency + high-difficulty topics
                   - Prioritizes long-term recurring topics
                
                4. **Evidence Citations** 📊
                   - Every insight includes: when, how often, and why
                   - See the data behind the recommendations
                
                5. **Trend Analysis** 📈
                   - Shows how topics change over time
                   - Identifies emerging important areas
                
                ### How to Use These Insights
                
                1. Start with **Study Strategy** for overall direction
                2. Review **Risk Areas** to focus on challenging topics
                3. Check **Topic Trends** for emerging patterns
                4. Use **Time Strategy** for exam day planning
                5. Combine all for comprehensive preparation
                """)
        
    except Exception as e:
        st.error(f"Error loading insights: {e}")
        logger.error(f"Insights page error: {e}")
