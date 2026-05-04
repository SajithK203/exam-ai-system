"""
Topic Classifier Module - Classify questions into topics.
Uses rules-based approach to identify question topics.
"""

import re
import logging
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class TopicClassifier:
    """Classify questions into topics using rule-based approach."""
    
    # Topic keywords mapping
    TOPIC_KEYWORDS = {
        'Binary Trees': ['binary tree', 'bst', 'traversal', 'inorder', 'preorder', 'postorder', 'tree structure'],
        'Linked Lists': ['linked list', 'node', 'pointer', 'single linked', 'doubly linked', 'circular linked'],
        'Graphs': ['graph', 'vertex', 'edge', 'directed graph', 'undirected', 'adjacency', 'dfs', 'bfs'],
        'Sorting Algorithms': ['sort', 'bubble sort', 'merge sort', 'quick sort', 'heap sort', 'insertion sort', 'selection sort'],
        'Searching Algorithms': ['search', 'binary search', 'linear search', 'sequential', 'find'],
        'Dynamic Programming': ['dynamic programming', 'dp', 'memoization', 'tabulation', 'optimization'],
        'Hash Tables': ['hash table', 'hash map', 'hashing', 'hash function', 'collision', 'load factor'],
        'Stacks & Queues': ['stack', 'queue', 'lifo', 'fifo', 'push', 'pop', 'enqueue', 'dequeue'],
        'String Manipulation': ['string', 'substring', 'pattern matching', 'palindrome', 'anagram'],
        'Database Design': ['database', 'normalization', 'schema', 'foreign key', 'primary key', 'sql'],
    }
    
    @staticmethod
    def classify_question(question_text):
        """
        Classify a question into a topic.
        
        Args:
            question_text: The question text
            
        Returns:
            Topic name (string) or None if not classified
        """
        try:
            question_lower = question_text.lower()
            max_matches = 0
            classified_topic = None
            
            # Count keyword matches for each topic
            for topic, keywords in TopicClassifier.TOPIC_KEYWORDS.items():
                matches = 0
                for keyword in keywords:
                    # Use word boundaries for better matching
                    if re.search(r'\b' + re.escape(keyword) + r'\b', question_lower):
                        matches += 1
                
                if matches > max_matches:
                    max_matches = matches
                    classified_topic = topic
            
            if classified_topic:
                logger.debug(f"Classified question to topic: {classified_topic}")
            else:
                logger.debug("Question could not be classified to any topic")
            
            return classified_topic
            
        except Exception as e:
            logger.error(f"Error classifying question: {e}")
            return None
    
    @staticmethod
    def classify_batch(questions_list):
        """
        Classify multiple questions.
        
        Args:
            questions_list: List of question text strings
            
        Returns:
            List of dictionaries with question and classified topic
        """
        try:
            results = []
            for question in questions_list:
                topic = TopicClassifier.classify_question(question)
                results.append({
                    'question': question,
                    'topic': topic,
                    'confidence': 'high' if topic else 'low'
                })
            
            logger.info(f"Classified {len(results)} questions in batch")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch classification: {e}")
            raise
    
    @staticmethod
    def get_topic_id_by_name(topic_name):
        """Get topic ID from database by name."""
        try:
            query = "SELECT id FROM topics WHERE topic_name = %s"
            result = DatabaseConnection.execute_query(query, (topic_name,), fetch_one=True)
            return result['id'] if result else None
        except Exception as e:
            logger.warning(f"Error getting topic ID: {e}")
            return None
    
    @staticmethod
    def create_missing_topic(topic_name):
        """Create a new topic in database if it doesn't exist."""
        try:
            # Check if exists
            existing = TopicClassifier.get_topic_id_by_name(topic_name)
            if existing:
                return existing
            
            # Create new
            query = "INSERT INTO topics (topic_name, category) VALUES (%s, %s)"
            DatabaseConnection.execute_query(query, (topic_name, 'Other'))
            logger.info(f"Created new topic: {topic_name}")
            
            # Return the ID
            return TopicClassifier.get_topic_id_by_name(topic_name)
            
        except Exception as e:
            logger.error(f"Error creating topic: {e}")
            return None
    
    @staticmethod
    def add_custom_keywords(topic_name, keywords):
        """
        Add custom keywords for a topic.
        
        Args:
            topic_name: Name of the topic
            keywords: List of keywords to add
        """
        try:
            if topic_name in TopicClassifier.TOPIC_KEYWORDS:
                TopicClassifier.TOPIC_KEYWORDS[topic_name].extend(keywords)
                logger.info(f"Added custom keywords for {topic_name}")
            else:
                TopicClassifier.TOPIC_KEYWORDS[topic_name] = keywords
                logger.info(f"Created new topic with keywords: {topic_name}")
        except Exception as e:
            logger.error(f"Error adding custom keywords: {e}")
            raise
    
    @staticmethod
    def suggest_topics(question_text, top_n=3):
        """
        Suggest top N topics for a question (with scores).
        
        Returns:
            List of tuples (topic, score)
        """
        try:
            question_lower = question_text.lower()
            scores = {}
            
            for topic, keywords in TopicClassifier.TOPIC_KEYWORDS.items():
                score = 0
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', question_lower):
                        score += 1
                
                if score > 0:
                    scores[topic] = score
            
            # Sort by score and return top N
            sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_topics[:top_n]
            
        except Exception as e:
            logger.error(f"Error suggesting topics: {e}")
            return []
    
    @staticmethod
    def get_all_topics():
        """Get all available topics from database."""
        try:
            query = "SELECT id, topic_name FROM topics ORDER BY topic_name"
            result = DatabaseConnection.execute_query(query, fetch_all=True)
            return result if result else []
        except Exception as e:
            logger.warning(f"Error getting all topics: {e}")
            return []
