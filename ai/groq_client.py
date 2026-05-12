"""
Groq API Client Module - Handle communication with Groq AI API.
Used for RAG-based insight generation.
"""

import logging
from groq import Groq
from config.settings import AI_CONFIG, GROQ_API_KEY

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for Groq API interactions."""
    
    def __init__(self):
        """Initialize Groq client."""
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = AI_CONFIG.get('model', 'llama-3.3-70b-versatile')  # Updated from deprecated llama-3-70b-versatile
        self.temperature = AI_CONFIG.get('temperature', 0.7)
        self.max_tokens = AI_CONFIG.get('max_tokens', 1000)
        self.top_p = AI_CONFIG.get('top_p', 1)
        
        logger.info(f"Groq client initialized with model: {self.model}")
    
    def generate_response(self, prompt, temperature=None, max_tokens=None):
        """
        Generate response from Groq API.
        
        Args:
            prompt: The prompt to send to AI
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Generated response text
        """
        try:
            temperature = temperature or self.temperature
            max_tokens = max_tokens or self.max_tokens
            
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.top_p
            )
            
            response_text = message.choices[0].message.content
            logger.debug(f"Generated response from Groq: {len(response_text)} chars")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response from Groq: {e}")
            raise
    
    def generate_study_recommendation(self, subject, topics_data):
        """
        Generate study recommendation based on topic data.
        
        Args:
            subject: Subject name
            topics_data: Dictionary with topic frequencies and questions
            
        Returns:
            AI-generated recommendation text
        """
        try:
            from ai.prompts import PromptTemplates
            
            prompt = PromptTemplates.get_study_recommendation_prompt(subject, topics_data)
            response = self.generate_response(prompt)
            
            logger.info(f"Generated study recommendation for {subject}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating study recommendation: {e}")
            raise
    
    def generate_insight(self, insight_type, data):
        """
        Generate AI insight of specified type.
        
        Args:
            insight_type: Type of insight ('topic_focus', 'trend', 'preparation', etc.)
            data: Data for generating insight
            
        Returns:
            Generated insight text
        """
        try:
            from ai.prompts import PromptTemplates
            
            prompt = PromptTemplates.get_prompt(insight_type, data)
            response = self.generate_response(prompt)
            
            logger.info(f"Generated {insight_type} insight")
            return response
            
        except Exception as e:
            logger.error(f"Error generating insight: {e}")
            raise
    
    def test_connection(self):
        """Test if API connection is working."""
        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'Connection successful' and nothing else."
                    }
                ],
                model=self.model,
                max_tokens=10
            )
            
            logger.info("Groq API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False


# Singleton instance
_groq_client = None


def reset_groq_client():
    """Reset the Groq client singleton (for testing/reloading)."""
    global _groq_client
    _groq_client = None


def get_groq_client():
    """Get or create Groq client instance."""
    global _groq_client
    if _groq_client is None:
        try:
            _groq_client = GroqClient()
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    return _groq_client
