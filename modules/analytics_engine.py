"""
Analytics Engine Module - Analyze patterns and generate statistics.
Provides high-level analytics on extracted data.
"""

import logging
from database.queries.analytics_queries import AnalyticsQueries

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Analyze exam data and generate insights."""
    
    @staticmethod
    def get_full_analysis(subject, years=None):
        """
        Get comprehensive analysis for a subject.
        
        Returns:
            Dictionary with all analytics data
        """
        try:
            analysis = {
                'subject': subject,
                'topic_frequency': AnalyticsQueries.get_topic_frequency(subject, years),
                'topic_trends': AnalyticsQueries.get_trending_topics(subject, years or 5),
                'top_topics': AnalyticsQueries.get_top_topics(subject, limit=10),
                'question_type_distribution': AnalyticsQueries.get_question_type_distribution(subject),
                'difficulty_distribution': AnalyticsQueries.get_difficulty_distribution(subject),
                'papers_per_year': AnalyticsQueries.get_papers_per_year(subject),
            }
            
            logger.info(f"Generated full analysis for {subject}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating full analysis: {e}")
            raise
    
    @staticmethod
    def get_study_focus_areas(subject, top_n=5):
        """
        Get top focus areas for studying.
        
        Returns:
            List of topics to focus on (sorted by frequency)
        """
        try:
            topics = AnalyticsQueries.get_top_topics(subject, limit=top_n)
            logger.info(f"Generated study focus areas for {subject}")
            return topics
        except Exception as e:
            logger.error(f"Error generating study focus areas: {e}")
            raise
    
    @staticmethod
    def get_repeated_questions_analysis():
        """
        Analyze questions that appear multiple times.
        
        Returns:
            List of repeated questions with frequency
        """
        try:
            repeated = AnalyticsQueries.get_repeated_questions()
            logger.info(f"Found {len(repeated)} repeated questions")
            return repeated
        except Exception as e:
            logger.error(f"Error analyzing repeated questions: {e}")
            raise
    
    @staticmethod
    def get_subject_comparison():
        """
        Compare statistics across all subjects.
        
        Returns:
            Subject statistics comparison
        """
        try:
            stats = AnalyticsQueries.get_subject_statistics()
            logger.info(f"Generated subject comparison for {len(stats)} subjects")
            return stats
        except Exception as e:
            logger.error(f"Error comparing subjects: {e}")
            raise
    
    @staticmethod
    def get_trend_analysis(subject, topic_id, years=10):
        """
        Get trend analysis for a specific topic over years.
        
        Returns:
            List of year-wise frequency data
        """
        try:
            trends = AnalyticsQueries.get_topic_trend_analysis(subject, topic_id, years)
            logger.info(f"Generated trend analysis for topic in {subject}")
            return trends
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            raise
    
    @staticmethod
    def get_recommendations_data(subject):
        """
        Get data to feed into AI for recommendations.
        
        Returns:
            Dictionary with key data points
        """
        try:
            top_topics = AnalyticsQueries.get_top_topics(subject, limit=5)
            repeated_questions = AnalyticsQueries.get_repeated_questions()
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            trends = AnalyticsQueries.get_papers_per_year(subject)
            
            data = {
                'subject': subject,
                'top_topics': top_topics,
                'repeated_questions': repeated_questions,
                'question_types': question_types,
                'paper_trends': trends,
            }
            
            logger.info(f"Prepared recommendations data for {subject}")
            return data
        except Exception as e:
            logger.error(f"Error preparing recommendations data: {e}")
            raise
    
    @staticmethod
    def format_analysis_for_display(analysis):
        """
        Format analysis results for display in UI.
        
        Returns:
            Formatted analysis data
        """
        try:
            formatted = {
                'subject': analysis.get('subject', 'Unknown'),
                'total_topics': len(analysis.get('topic_frequency', [])),
                'top_5_topics': analysis.get('top_topics', [])[:5],
                'question_types': analysis.get('question_type_distribution', []),
                'difficulty_levels': analysis.get('difficulty_distribution', []),
                'papers_timeline': analysis.get('papers_per_year', []),
            }
            
            logger.debug("Formatted analysis for display")
            return formatted
        except Exception as e:
            logger.error(f"Error formatting analysis: {e}")
            raise
