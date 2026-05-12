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
        Generate evidence-based study plan with topic intelligence scores.
        
        Args:
            subject: Subject name
            
        Returns:
            Dictionary with evidence-backed study plan
        """
        try:
            # Get evidence data
            top_topics = AnalyticsQueries.get_top_topics(subject, limit=15)
            trending_topics = AnalyticsQueries.get_trending_topics(subject, years=5)
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            
            # Calculate topic intelligence scores
            scored_topics = []
            for topic in top_topics:
                topic_name = topic['topic_name']
                frequency = topic['frequency']
                
                # Calculate trend (increase = positive)
                trend_score = 0
                for trend in trending_topics:
                    if trend.get('topic_name') == topic_name:
                        trend_score = trend.get('frequency', 0) * 5  # Recent weight
                
                # Intelligence score = frequency + trend
                intelligence_score = min(100, (frequency * 4) + trend_score)
                
                scored_topics.append({
                    **topic,
                    'intelligence_score': intelligence_score,
                    'confidence': 'High' if frequency >= 5 else 'Medium' if frequency >= 2 else 'Low'
                })
            
            # Sort by intelligence score
            scored_topics.sort(key=lambda x: x['intelligence_score'], reverse=True)
            
            # Prepare evidence for AI
            topics_data = {
                'top_topics': scored_topics[:10],
                'question_types': question_types,
                'total_topics_analyzed': len(top_topics)
            }
            
            # Get AI recommendation with evidence
            groq = get_groq_client()
            recommendation = groq.generate_study_recommendation(subject, topics_data)
            
            study_plan = {
                'subject': subject,
                'top_topics': scored_topics[:5],
                'medium_priority': scored_topics[5:10],
                'topic_intelligence_scores': scored_topics[:10],
                'ai_recommendation': recommendation,
                'confidence': 'High' if len(scored_topics) > 5 else 'Medium',
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated evidence-based study plan for {subject}")
            return study_plan
            
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            raise
    
    @staticmethod
    def generate_mock_exam_suggestions(subject):
        """
        Generate mock exam suggestions using REAL questions with evidence.
        Selects questions based on: topic importance, difficulty balance, recency.
        
        Args:
            subject: Subject name
            
        Returns:
            Dictionary with mock exam recommendations and real question examples
        """
        try:
            from database.queries.question_queries import QuestionQueries
            
            # Get analysis data
            top_topics = AnalyticsQueries.get_top_topics(subject, limit=10)
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            difficulty = AnalyticsQueries.get_difficulty_distribution(subject)
            
            # Get real questions from top topics for mock exam
            mock_exam_structure = []
            real_question_samples = []
            
            for i, topic in enumerate(top_topics[:5]):  # Top 5 topics
                topic_name = topic['topic_name']
                frequency = topic['frequency']
                
                # Calculate questions to include in mock (based on importance)
                questions_count = max(2, int(frequency / 2))
                
                # Get real questions for this topic
                topic_questions = QuestionQueries.get_questions_by_topic_with_subject(subject, topic_name, limit=5)
                
                if topic_questions:
                    real_question_samples.extend(topic_questions[:questions_count])
                
                mock_exam_structure.append({
                    'topic': topic_name,
                    'frequency': frequency,
                    'recommended_questions': questions_count,
                    'difficulty_suggestion': 'Mixed' if frequency >= 5 else 'Medium'
                })
            
            # Get AI suggestions with evidence
            groq = get_groq_client()
            
            prompt = f"""Based ONLY on the following evidence, create a mock exam structure for {subject}:

TOPIC IMPORTANCE (based on frequency analysis):
"""
            for item in mock_exam_structure:
                prompt += f"- {item['topic']}: {item['recommended_questions']} questions (appeared {item['frequency']} times)\n"
            
            prompt += f"""
QUESTION TYPE DISTRIBUTION:
"""
            for qtype in question_types:
                prompt += f"- {qtype['question_type']}: {qtype['percentage']}%\n"
            
            prompt += f"""
DIFFICULTY DISTRIBUTION:
"""
            for diff in difficulty:
                prompt += f"- {diff['difficulty_level']}: Include {diff.get('count', 0)} questions\n"
            
            prompt += f"""
Based ONLY on this evidence, provide:
1. Complete mock exam structure with topic allocation
2. Recommended difficulty mix
3. Total marks suggestion
4. Estimated time (in minutes)
5. Why this structure matches actual exam patterns

Reference the data provided. Do NOT suggest random topics."""
            
            suggestions = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'suggestions': suggestions,
                'recommended_topics': mock_exam_structure,
                'sample_questions': real_question_samples[:10],  # Include real question samples
                'confidence': 'High' if len(real_question_samples) >= 10 else 'Medium',
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated evidence-based mock exam suggestions for {subject}")
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
            
            from database.queries.question_queries import QuestionQueries
            # FIX: get_questions_by_topic is in QuestionQueries, not AnalyticsQueries
            questions = QuestionQueries.get_questions_by_topic(topic_id, limit=10)
            trends = AnalyticsQueries.get_topic_trend_analysis(subject, topic_id)
            
            frequency = len(questions)
            
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
        Identify weak areas with evidence-based intelligent scoring.
        Combines: frequency × difficulty × recurrence
        
        Args:
            subject: Subject name
            
        Returns:
            Analysis of weak areas with supporting evidence
        """
        try:
            # Get weak areas with intelligent scoring
            weak_areas_scored = AnalyticsQueries.get_weak_areas_scored(subject, years=5)
            
            # Get top weak areas
            top_weak_areas = weak_areas_scored[:10] if weak_areas_scored else []
            
            # Build evidence summary
            weak_areas_evidence = []
            for area in top_weak_areas:
                weak_areas_evidence.append({
                    'topic': area.get('topic_name'),
                    'frequency': area.get('frequency'),
                    'years_appeared': area.get('years_appeared'),
                    'difficulty_level': area.get('avg_difficulty'),
                    'importance_score': area.get('importance_score')
                })
            
            # Get AI analysis with evidence
            groq = get_groq_client()
            
            prompt = f"""Based ONLY on the following evidence, identify weak areas in {subject} that need focus:

WEAK AREAS (ranked by difficulty × frequency × recurrence):
"""
            for i, area in enumerate(weak_areas_evidence[:5], 1):
                prompt += f"""
{i}. {area['topic']}
   - Frequency: {area['frequency']} questions
   - Years appeared: {area['years_appeared']} years
   - Avg difficulty level: {area['difficulty_level']:.1f}/3
   - Importance score: {area['importance_score']:.2f}
"""
            
            prompt += f"""
Based ONLY on this evidence, provide:
1. Top 3 weak areas with specific reasons (cite the data)
2. Why these areas are challenging
3. Targeted improvement strategy for each
4. Confidence level in this assessment (High/Medium/Low)

Do NOT provide generic advice. Reference the numbers and patterns shown."""
            
            analysis = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'weak_areas_ranked': weak_areas_evidence,
                'analysis': analysis,
                'confidence': 'High' if len(weak_areas_evidence) >= 5 else 'Medium',
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated evidence-based weak area analysis for {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating weak area analysis: {e}")
            raise
    
    @staticmethod
    def generate_time_management_plan(subject):
        """
        Generate evidence-based time management and pacing strategy.
        
        Args:
            subject: Subject name
            
        Returns:
            Time management recommendations with evidence
        """
        try:
            # Get exam statistics
            stats = AnalyticsQueries.get_subject_statistics()
            subject_stat = next((s for s in stats if s['subject'] == subject), None)
            
            if not subject_stat:
                raise ValueError(f"No data for subject: {subject}")
            
            # Get question type distribution
            question_types = AnalyticsQueries.get_question_type_distribution(subject)
            
            # Get difficulty distribution
            difficulty = AnalyticsQueries.get_difficulty_distribution(subject)
            
            groq = get_groq_client()
            
            prompt = f"""Create a data-driven time management strategy for {subject} based on ONLY this evidence:

EXAM STATISTICS:
- Total Papers Analyzed: {subject_stat['total_papers']}
- Total Questions: {subject_stat['total_questions']}
- Average per Paper: {subject_stat['avg_questions_per_paper']:.1f}
- Years Covered: {subject_stat['years_covered']} years

QUESTION DISTRIBUTION:
"""
            for qtype in question_types:
                prompt += f"- {qtype['question_type']}: {qtype['count']} questions ({qtype['percentage']}%)\n"
            
            prompt += "\nDIFFICULTY DISTRIBUTION:\n"
            for diff in difficulty:
                prompt += f"- {diff['difficulty_level']}: {diff['count']} questions\n"
            
            prompt += f"""
Based ONLY on this evidence, provide:
1. Recommended time per question (in minutes)
2. How to allocate time across question types
3. Section-wise strategy
4. Revision time recommendation
5. Confidence level in these recommendations

Be specific and cite the data provided. Do NOT provide generic advice."""
            
            strategy = groq.generate_response(prompt)
            
            result = {
                'subject': subject,
                'strategy': strategy,
                'exam_stats': subject_stat,
                'question_distribution': question_types,
                'difficulty_distribution': difficulty,
                'confidence': 'High' if subject_stat['total_papers'] >= 10 else 'Medium',
                'generated_at': __import__('datetime').datetime.now().isoformat()
            }
            
            logger.info(f"Generated evidence-based time management plan for {subject}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating time management plan: {e}")
            raise
