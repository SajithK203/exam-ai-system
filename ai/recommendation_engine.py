"""
Recommendation Engine Module - Generate smart study recommendations.
Combines analytics data with AI to produce actionable recommendations.
"""

import logging
from ai.groq_client import get_groq_client
from modules.analytics_engine import AnalyticsEngine
from database.queries.analytics_queries import AnalyticsQueries

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate personalized study recommendations."""
    
    @staticmethod
    def generate_study_plan(subject):
        """
        Generate comprehensive study plan for a subject.
        
        Args:
            subject: Subject name
            
        Returns:
            Dictionary with study plan
        """
        try:
            # Get analytics data
            top_topics = AnalyticsQueries.get_top_topics(subject, limit=10)
            repeated_questions = AnalyticsQueries.get_repeated_questions()
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            
            # Prepare data for AI
            topics_data = {
                'top_topics': top_topics,
                'repeated_questions': repeated_questions,
                'question_types': question_types,
            }
            
            # Get AI recommendation
            groq = get_groq_client()
            recommendation = groq.generate_study_recommendation(subject, topics_data)
            
            study_plan = {
                'subject': subject,
                'top_topics': top_topics[:5],
                'ai_recommendation': recommendation,
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated study plan for {subject}")
            return study_plan
            
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            raise
    
    @staticmethod
    def generate_mock_exam_suggestions(subject):
        """
        Generate suggestions for mock exam creation.
        
        Args:
            subject: Subject name
            
        Returns:
            Dictionary with mock exam suggestions
        """
        try:
            # Get analysis data
            top_topics = AnalyticsQueries.get_top_topics(subject, limit=5)
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            difficulty = AnalyticsQueries.get_difficulty_distribution(subject)
            
            # Prepare AI prompt
            exam_data = {
                'top_topics': top_topics,
                'question_types': question_types,
                'difficulty_levels': difficulty,
            }
            
            groq = get_groq_client()
            suggestions = groq.generate_insight('mock_exam', exam_data)
            
            result = {
                'subject': subject,
                'suggestions': suggestions,
                'recommended_topics': top_topics,
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated mock exam suggestions for {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating mock exam suggestions: {e}")
            raise
    
    @staticmethod
    def generate_topic_focus_guide(subject, topic_name):
        """
        Generate focused study guide for a specific topic.
        
        Args:
            subject: Subject name
            topic_name: Topic to focus on
            
        Returns:
            Detailed focus guide
        """
        try:
            # Get topic data
            from modules.topic_classifier import TopicClassifier
            topic_id = TopicClassifier.get_topic_id_by_name(topic_name)
            
            if not topic_id:
                raise ValueError(f"Topic not found: {topic_name}")
            
            questions = AnalyticsQueries.get_questions_by_topic(topic_id)
            trends = AnalyticsQueries.get_topic_trend_analysis(subject, topic_id)
            
            frequency = sum(1 for q in questions)
            
            # Get AI guidance
            groq = get_groq_client()
            prompt = f"""Provide comprehensive focus guide for {topic_name} in {subject}:
- Appears {frequency} times in exams
- Trend data: {trends}
- Sample questions: {len(questions)}

Cover: key concepts, common mistakes, practice tips."""
            
            guide = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'topic': topic_name,
                'frequency': frequency,
                'guide': guide,
                'related_questions': len(questions),
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated focus guide for {topic_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating topic focus guide: {e}")
            raise
    
    @staticmethod
    def generate_weak_area_analysis(subject):
        """
        Identify and provide recommendations for weak areas.
        
        Args:
            subject: Subject name
            
        Returns:
            Analysis of weak areas
        """
        try:
            # Get comprehensive analysis
            analysis = AnalyticsEngine.get_full_analysis(subject)
            
            groq = get_groq_client()
            
            prompt = f"""Based on {subject} exam patterns, identify potential weak areas and provide targeted improvement strategies:

Data: {analysis}

Provide: 1) Weak areas students typically struggle with, 2) Why they're important, 3) How to overcome them"""
            
            weak_areas = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'analysis': weak_areas,
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated weak area analysis for {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating weak area analysis: {e}")
            raise
    
    @staticmethod
    def generate_time_management_plan(subject):
        """
        Generate time management and pacing strategy.
        
        Args:
            subject: Subject name
            
        Returns:
            Time management recommendations
        """
        try:
            # Get exam statistics
            stats = AnalyticsQueries.get_subject_statistics()
            subject_stat = next((s for s in stats if s['subject'] == subject), None)
            
            if not subject_stat:
                raise ValueError(f"No data for subject: {subject}")
            
            groq = get_groq_client()
            
            prompt = f"""Create a time management strategy for {subject}:
- Papers: {subject_stat['total_papers']}
- Questions: {subject_stat['total_questions']}
- Avg per paper: {subject_stat['avg_questions_per_paper']}

Provide: time per question, section strategy, revision time."""
            
            strategy = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'strategy': strategy,
                'exam_stats': subject_stat,
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated time management plan for {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating time management plan: {e}")
            raise
