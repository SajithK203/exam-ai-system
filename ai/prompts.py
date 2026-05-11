"""
Prompt Templates Module - Define prompts for AI interactions.
Used to generate consistent and effective prompts for Groq API.
"""

import logging
import json
from utils.serializer import sanitize

logger = logging.getLogger(__name__)


class PromptTemplates:
    """Collection of prompt templates for AI interactions."""
    
    @staticmethod
    def get_study_recommendation_prompt(subject, topics_data):
        """
        Generate prompt for evidence-based study recommendation.
        
        Args:
            subject: Subject name
            topics_data: Dictionary with topic analysis including intelligence scores
            
        Returns:
            Formatted prompt
        """
        try:
            top_topics = topics_data.get('top_topics', [])
            repeated_questions = topics_data.get('repeated_questions', [])
            total_analyzed = topics_data.get('total_topics_analyzed', 0)
            
            topics_text = ""
            for t in top_topics[:10]:
                score = t.get('intelligence_score', t.get('frequency', 0))
                topics_text += f"- {t['topic_name']}: {t['frequency']} times (Score: {score:.0f})\n"
            
            prompt = f"""Based ONLY on the following evidence, provide focused study recommendations for {subject}:

EVIDENCE DATA:
Total Topics Analyzed: {total_analyzed}

Top Priority Topics (by intelligence score):
{topics_text}

Repeated/Important Questions Found: {len(repeated_questions)}

Instructions:
1. Rank the topics by importance using ONLY the scores and frequencies provided
2. Cite specific numbers for each recommendation
3. Explain WHY each topic matters based on appearance frequency
4. Suggest study approach based on patterns
5. Estimate time allocation based on importance score

CRITICAL: Do NOT provide generic study tips. Every recommendation must cite the data."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating study recommendation prompt: {e}")
            raise
    
    @staticmethod
    def get_topic_focus_prompt(subject, topic_name, frequency, questions):
        """Generate prompt for topic-specific focus."""
        try:
            sample_questions = questions[:3] if questions else []
            
            prompt = f"""For {subject} exam preparation, analyze the topic '{topic_name}':

Frequency: Asked {frequency} times in past papers
Sample Questions: {len(questions)} questions found

Key Learning Points and Study Strategy:
- What are the most important concepts in {topic_name}?
- How frequently does this topic appear?
- What related topics should be studied together?
- Recommended study resources and practice approach

Provide a structured study guide."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating topic focus prompt: {e}")
            raise
    
    @staticmethod
    def get_mock_exam_generation_prompt(subject, top_topics, difficulty_distribution):
        """Generate prompt for mock exam suggestions."""
        try:
            topics_text = "\\n".join([t['topic_name'] for t in top_topics[:5]])
            
            prompt = f"""Generate a mock exam structure for {subject} based on historical patterns:

Most Important Topics:
{topics_text}

Create a suggested mock exam with:
1. Number of questions from each topic
2. Recommended difficulty distribution (Easy/Medium/Hard)
3. Question type mix (MCQ/Short Answer/Long Answer)
4. Total marks allocation
5. Suggested time duration

Ensure the mock exam matches typical exam patterns."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating mock exam prompt: {e}")
            raise
    
    @staticmethod
    def get_trend_analysis_prompt(subject, trends_data):
        """Generate prompt for trend analysis."""
        try:
            # Sanitize data to handle numpy types
            trends_data = sanitize(trends_data)
            
            prompt = f"""Analyze the examination trends for {subject}:

Analysis Data:
{json.dumps(trends_data, indent=2)}

Provide insights on:
1. Which topics are trending up/down?
2. Significant pattern changes over years
3. Emerging topics to focus on
4. Declining but still important topics
5. Future exam predictions

Be specific and data-driven."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating trend analysis prompt: {e}")
            raise
    
    @staticmethod
    def get_weakness_identification_prompt(subject, topics_data, performance_data):
        """Generate prompt to identify weak areas."""
        try:
            # Sanitize data to handle numpy types
            topics_data = sanitize(topics_data)
            
            prompt = f"""Based on {subject} exam data, identify potential weak areas:

Most Frequently Asked Topics:
{json.dumps(topics_data, indent=2)}

Please identify:
1. High-frequency topics that students typically struggle with
2. Complex interconnected topics
3. Lesser-known concepts that appear in exams
4. Topics with rapid difficulty escalation
5. Recommended extra focus areas

Provide actionable guidance."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating weakness identification prompt: {e}")
            raise
    
    @staticmethod
    def get_exam_strategy_prompt(subject, exam_analysis):
        """Generate prompt for exam strategy recommendations."""
        try:
            # Sanitize data to handle numpy types
            exam_analysis = sanitize(exam_analysis)
            
            prompt = f"""Provide an exam strategy for {subject} based on historical analysis:

Exam Characteristics:
{json.dumps(exam_analysis, indent=2)}

Develop a strategy covering:
1. Time management per question type
2. Which topics to attempt first
3. Difficulty level navigation
4. Common pitfalls to avoid
5. Last-minute revision focus areas
6. Test-taking tips specific to this subject

Make it practical and specific."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating exam strategy prompt: {e}")
            raise
    
    @staticmethod
    def get_prompt(prompt_type, data):
        """
        Get prompt based on type.
        
        Args:
            prompt_type: Type of prompt needed
            data: Data to include in prompt
            
        Returns:
            Formatted prompt
        """
        try:
            prompts = {
                'study_recommendation': PromptTemplates._generic_recommendation,
                'topic_focus': PromptTemplates._generic_topic_focus,
                'mock_exam': PromptTemplates._generic_mock_exam,
                'trend': PromptTemplates._generic_trend,
                'strategy': PromptTemplates._generic_strategy,
            }
            
            if prompt_type in prompts:
                return prompts[prompt_type](data)
            else:
                logger.warning(f"Unknown prompt type: {prompt_type}")
                return "Please provide relevant data for analysis."
                
        except Exception as e:
            logger.error(f"Error getting prompt: {e}")
            raise
    
    @staticmethod
    def _generic_recommendation(data):
        """Generic recommendation prompt."""
        subject = data.get('subject', 'Unknown Subject')
        return f"Provide study recommendations for {subject} based on the following data: {json.dumps(data)}"
    
    @staticmethod
    def _generic_topic_focus(data):
        """Generic topic focus prompt."""
        topic = data.get('topic', 'Unknown')
        return f"Provide detailed focus guidelines for the topic: {topic}"
    
    @staticmethod
    def _generic_mock_exam(data):
        """Generic mock exam prompt."""
        subject = data.get('subject', 'Unknown')
        return f"Suggest a mock exam structure for {subject} based on: {json.dumps(data)}"
    
    @staticmethod
    def _generic_trend(data):
        """Generic trend prompt."""
        return f"Analyze the following trend data and provide insights: {json.dumps(data)}"
    
    @staticmethod
    def _generic_strategy(data):
        """Generic strategy prompt."""
        subject = data.get('subject', 'Unknown')
        return f"Develop an exam strategy for {subject}: {json.dumps(data)}"
