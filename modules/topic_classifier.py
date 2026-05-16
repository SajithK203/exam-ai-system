"""
Topic Classifier Module - Classify questions into topics.
Uses a hybrid approach:
  1. Rule-based keyword matching (fast, explainable)
  2. AI fallback via Groq when keyword confidence is zero
"""

import re
import logging
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cognitive verb → difficulty mapping used by infer_difficulty()
# ---------------------------------------------------------------------------
_EASY_VERBS = re.compile(
    r'\b(define|list|name|state|identify|recall|what is|what are|write down|mention|describe)\b',
    re.IGNORECASE,
)
_MEDIUM_VERBS = re.compile(
    r'\b(explain|compare|contrast|summarize|illustrate|classify|differentiate|outline|discuss)\b',
    re.IGNORECASE,
)
_HARD_VERBS = re.compile(
    r'\b(design|implement|develop|analyze|evaluate|critique|justify|construct|derive|prove|optimize|create|build)\b',
    re.IGNORECASE,
)


class TopicClassifier:
    """Classify questions into topics using hybrid rule-based + AI approach."""

    # Topic keywords mapping — extend freely
    TOPIC_KEYWORDS = {
        'Binary Trees': ['binary tree', 'bst', 'traversal', 'inorder', 'preorder', 'postorder', 'tree structure', 'avl', 'red black tree', 'heap'],
        'Linked Lists': ['linked list', 'node', 'pointer', 'single linked', 'doubly linked', 'circular linked', 'singly linked'],
        'Graphs': ['graph', 'vertex', 'edge', 'directed graph', 'undirected', 'adjacency', 'dfs', 'bfs', 'shortest path', 'dijkstra', 'bellman', 'floyd'],
        'Sorting Algorithms': ['sort', 'bubble sort', 'merge sort', 'quick sort', 'heap sort', 'insertion sort', 'selection sort', 'radix sort', 'counting sort'],
        'Searching Algorithms': ['search', 'binary search', 'linear search', 'sequential', 'find element', 'lookup'],
        'Dynamic Programming': ['dynamic programming', 'dp ', 'memoization', 'tabulation', 'optimal substructure', 'overlapping subproblems', 'knapsack', 'longest common subsequence'],
        'Hash Tables': ['hash table', 'hash map', 'hashing', 'hash function', 'collision', 'load factor', 'chaining', 'open addressing'],
        'Stacks & Queues': ['stack', 'queue', 'lifo', 'fifo', 'push', 'pop', 'enqueue', 'dequeue', 'priority queue', 'deque'],
        'String Manipulation': ['string', 'substring', 'pattern matching', 'palindrome', 'anagram', 'regular expression', 'kmp', 'rabin karp'],
        'Database Design': ['database', 'normalization', 'schema', 'foreign key', 'primary key', 'sql', 'erd', 'entity relationship', 'transaction', 'acid'],
        'Object Oriented Programming': ['class', 'object', 'inheritance', 'polymorphism', 'encapsulation', 'abstraction', 'interface', 'constructor', 'overloading', 'overriding'],
        'Operating Systems': ['process', 'thread', 'deadlock', 'semaphore', 'mutex', 'scheduler', 'memory management', 'paging', 'segmentation', 'virtual memory'],
        'Computer Networks': ['tcp', 'udp', 'ip address', 'router', 'protocol', 'http', 'dns', 'osi model', 'bandwidth', 'latency'],
        'Software Engineering': ['agile', 'scrum', 'sdlc', 'software development', 'design pattern', 'solid principle', 'unit test', 'refactoring', 'uml'],
    }

    @staticmethod
    def classify_question(question_text, use_ai_fallback=True):
        """
        Classify a question into a topic using rule-based matching.
        Falls back to AI classification when keyword score is 0.

        Args:
            question_text: The question text
            use_ai_fallback: Whether to call Groq AI when no keywords match

        Returns:
            Tuple (topic_name: str | None, confidence: float, ai_used: bool)
        """
        try:
            question_lower = question_text.lower()
            scores = {}

            for topic, keywords in TopicClassifier.TOPIC_KEYWORDS.items():
                score = sum(
                    1 for kw in keywords
                    if re.search(r'\b' + re.escape(kw) + r'\b', question_lower)
                )
                if score > 0:
                    scores[topic] = score

            if scores:
                best_topic = max(scores, key=scores.__getitem__)
                total = sum(scores.values())
                confidence = round(scores[best_topic] / total, 2) if total else 0.0
                logger.debug(f"Rule-based: '{best_topic}' (conf={confidence})")
                return best_topic, confidence, False

            # --- AI fallback ---
            if use_ai_fallback:
                ai_topic = TopicClassifier._ai_classify(question_text)
                if ai_topic:
                    logger.debug(f"AI fallback classified: '{ai_topic}'")
                    return ai_topic, 0.6, True  # Fixed confidence for AI-classified

            logger.debug("Question could not be classified")
            return None, 0.0, False

        except Exception as e:
            logger.error(f"Error classifying question: {e}")
            return None, 0.0, False

    @staticmethod
    def _ai_classify(question_text):
        """Call Groq AI to classify a question into a topic."""
        try:
            from ai.groq_client import get_groq_client
            client = get_groq_client()
            topics_list = ', '.join(TopicClassifier.TOPIC_KEYWORDS.keys())
            prompt = (
                f"You are an academic topic classifier. Given the exam question below, "
                f"identify which ONE topic it belongs to from this list: {topics_list}. "
                f"If none match well, suggest a short topic name (max 3 words). "
                f"Reply with ONLY the topic name, nothing else.\n\n"
                f"Question: {question_text[:500]}"
            )
            response = client.generate_response(prompt, temperature=0.1, max_tokens=20)
            topic = response.strip().strip('"').strip("'")
            return topic if topic else None
        except Exception as e:
            logger.warning(f"AI classification fallback failed: {e}")
            return None

    @staticmethod
    def infer_difficulty(question_text, marks=None):
        """
        Infer difficulty level from cognitive verbs, question length, and marks.

        Cognitive verb mapping:
            Easy  → define, list, name, state, identify, recall
            Medium → explain, compare, classify, differentiate
            Hard  → design, implement, analyze, evaluate, justify

        Args:
            question_text: The question text
            marks: Marks allocated (optional, used as tiebreaker)

        Returns:
            'Easy' | 'Medium' | 'Hard'
        """
        try:
            if _HARD_VERBS.search(question_text):
                return 'Hard'
            if _EASY_VERBS.search(question_text):
                difficulty = 'Easy'
            elif _MEDIUM_VERBS.search(question_text):
                difficulty = 'Medium'
            else:
                # Fall back to marks / word count heuristic
                word_count = len(question_text.split())
                if marks is not None:
                    if marks >= 10:
                        return 'Hard'
                    elif marks >= 5:
                        return 'Medium'
                    else:
                        return 'Easy'
                # Word count heuristic
                if word_count > 60:
                    return 'Hard'
                elif word_count > 25:
                    return 'Medium'
                else:
                    return 'Easy'

            # Upgrade difficulty based on marks if we have them
            if marks is not None and marks >= 10 and difficulty == 'Easy':
                return 'Medium'
            if marks is not None and marks >= 15:
                return 'Hard'

            return difficulty

        except Exception as e:
            logger.warning(f"Error inferring difficulty: {e}")
            return 'Medium'

    # ------------------------------------------------------------------
    # Legacy compatibility — old code called classify_question() expecting
    # just a string return. We keep a simple wrapper.
    # ------------------------------------------------------------------
    @staticmethod
    def classify_question_simple(question_text):
        """Legacy: return just the topic name (or None). Use classify_question() for full info."""
        topic, _, _ = TopicClassifier.classify_question(question_text)
        return topic

    @staticmethod
    def classify_batch(questions_list):
        """
        Classify multiple questions.

        Returns:
            List of dicts: {question, topic, confidence, ai_used}
        """
        try:
            results = []
            for question in questions_list:
                topic, confidence, ai_used = TopicClassifier.classify_question(question)
                results.append({
                    'question': question,
                    'topic': topic,
                    'confidence': confidence,
                    'ai_used': ai_used,
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
            existing = TopicClassifier.get_topic_id_by_name(topic_name)
            if existing:
                return existing
            query = "INSERT INTO topics (topic_name, category) VALUES (%s, %s)"
            DatabaseConnection.execute_query(query, (topic_name, 'Other'))
            logger.info(f"Created new topic: {topic_name}")
            return TopicClassifier.get_topic_id_by_name(topic_name)
        except Exception as e:
            logger.error(f"Error creating topic: {e}")
            return None

    @staticmethod
    def add_custom_keywords(topic_name, keywords):
        """Add custom keywords for a topic at runtime."""
        try:
            if topic_name in TopicClassifier.TOPIC_KEYWORDS:
                TopicClassifier.TOPIC_KEYWORDS[topic_name].extend(keywords)
            else:
                TopicClassifier.TOPIC_KEYWORDS[topic_name] = keywords
            logger.info(f"Added keywords for '{topic_name}'")
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
                score = sum(
                    1 for kw in keywords
                    if re.search(r'\b' + re.escape(kw) + r'\b', question_lower)
                )
                if score > 0:
                    scores[topic] = score
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
