"""
Question Assistant AI Module
Provides AI-powered Q&A, MCQ explanation, and topic classification
using the Groq LLM client.
"""

import logging
from ai.groq_client import get_groq_client

logger = logging.getLogger(__name__)


class QuestionAssistant:
    """AI-powered assistant for answering and explaining exam questions."""

    # -------------------------------------------------------------------------
    # Answer + Explanation
    # -------------------------------------------------------------------------

    @staticmethod
    def get_answer_and_explanation(question_text, subject=None, topic=None):
        """
        Generate a full answer and explanation for an exam question.

        Args:
            question_text: The full question text
            subject: Subject name (optional, improves quality)
            topic: Topic name (optional, improves quality)

        Returns:
            dict: {
                'answer': str,       # Concise direct answer
                'explanation': str,  # Full explanation
                'key_points': str,   # Bullet points of key concepts
                'study_tip': str     # One study tip related to this question
            }
        """
        context = ""
        if subject:
            context += f"Subject: {subject}\n"
        if topic:
            context += f"Topic: {topic}\n"

        prompt = f"""You are an expert academic tutor. A student is studying for their exam and needs help with the following question.

{context}
Question: {question_text}

Please provide:
1. ANSWER: A clear, concise answer (2-4 sentences)
2. EXPLANATION: A thorough explanation of the concept (4-6 sentences)
3. KEY POINTS: 3-5 bullet points of the most important concepts to remember
4. STUDY TIP: One practical study tip for this topic

Format your response EXACTLY like this:
ANSWER:
[your answer here]

EXPLANATION:
[your explanation here]

KEY POINTS:
• [point 1]
• [point 2]
• [point 3]

STUDY TIP:
[your tip here]"""

        try:
            client = get_groq_client()
            response = client.generate_response(prompt, temperature=0.3, max_tokens=800)
            return QuestionAssistant._parse_answer_response(response)
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return {
                'answer': 'Unable to generate answer at this time.',
                'explanation': str(e),
                'key_points': '',
                'study_tip': ''
            }

    @staticmethod
    def _parse_answer_response(response_text):
        """Parse the structured AI response into sections."""
        result = {
            'answer': '',
            'explanation': '',
            'key_points': '',
            'study_tip': ''
        }
        try:
            sections = {
                'answer': 'ANSWER:',
                'explanation': 'EXPLANATION:',
                'key_points': 'KEY POINTS:',
                'study_tip': 'STUDY TIP:'
            }
            section_order = list(sections.keys())
            markers = list(sections.values())

            for i, (key, marker) in enumerate(sections.items()):
                start = response_text.find(marker)
                if start == -1:
                    continue
                start += len(marker)

                # Find end (start of next section)
                end = len(response_text)
                for next_marker in markers[i + 1:]:
                    next_pos = response_text.find(next_marker, start)
                    if next_pos != -1:
                        end = min(end, next_pos)

                result[key] = response_text[start:end].strip()

        except Exception as e:
            logger.warning(f"Error parsing answer response: {e}")
            result['answer'] = response_text.strip()

        return result

    # -------------------------------------------------------------------------
    # MCQ Explanation
    # -------------------------------------------------------------------------

    @staticmethod
    def get_mcq_explanation(question_text, options, selected_label=None,
                            subject=None, topic=None):
        """
        Generate an explanation for an MCQ question, identifying the correct answer
        and explaining why each option is correct or incorrect.

        Args:
            question_text: The question text (without options)
            options: List of dicts [{'label': 'A', 'text': '...'}, ...]
            selected_label: The option label the student selected (optional)
            subject: Subject name (optional)
            topic: Topic name (optional)

        Returns:
            dict: {
                'correct_label': str,         # e.g. 'B'
                'correct_text': str,          # text of correct option
                'is_correct': bool | None,    # whether student's answer was correct
                'explanation': str,           # full explanation
                'option_explanations': dict   # {'A': '...', 'B': '...', ...}
            }
        """
        options_text = "\n".join([f"{o['label']}) {o['text']}" for o in options])
        context = ""
        if subject:
            context += f"Subject: {subject}\n"
        if topic:
            context += f"Topic: {topic}\n"

        prompt = f"""You are an expert academic tutor. Analyze this multiple choice question and identify the correct answer.

{context}
Question: {question_text}

Options:
{options_text}

Please respond in EXACTLY this format:
CORRECT: [just the letter, e.g. A]

EXPLANATION:
[2-3 sentence explanation of why the correct answer is right]

OPTION A:
[one sentence why A is correct or incorrect]

OPTION B:
[one sentence why B is correct or incorrect]

OPTION C:
[one sentence why C is correct or incorrect]

OPTION D:
[one sentence why D is correct or incorrect]"""

        try:
            client = get_groq_client()
            response = client.generate_response(prompt, temperature=0.1, max_tokens=600)
            return QuestionAssistant._parse_mcq_response(response, options, selected_label)
        except Exception as e:
            logger.error(f"Error getting MCQ explanation: {e}")
            return {
                'correct_label': None,
                'correct_text': None,
                'is_correct': None,
                'explanation': f'Unable to generate explanation: {e}',
                'option_explanations': {}
            }

    @staticmethod
    def _parse_mcq_response(response_text, options, selected_label):
        """Parse the structured MCQ AI response."""
        result = {
            'correct_label': None,
            'correct_text': None,
            'is_correct': None,
            'explanation': '',
            'option_explanations': {}
        }

        try:
            # Extract correct answer
            import re
            correct_match = re.search(r'CORRECT:\s*([A-Da-d])', response_text)
            if correct_match:
                correct_label = correct_match.group(1).upper()
                result['correct_label'] = correct_label

                # Find correct option text
                for opt in options:
                    if opt['label'].upper() == correct_label:
                        result['correct_text'] = opt['text']
                        break

                # Evaluate student's answer
                if selected_label:
                    result['is_correct'] = selected_label.upper() == correct_label

            # Extract main explanation
            exp_match = re.search(r'EXPLANATION:\s*(.*?)(?=OPTION [A-D]:|$)', response_text, re.DOTALL)
            if exp_match:
                result['explanation'] = exp_match.group(1).strip()

            # Extract per-option explanations
            for label in ['A', 'B', 'C', 'D']:
                opt_match = re.search(
                    rf'OPTION {label}:\s*(.*?)(?=OPTION [A-D]:|$)',
                    response_text, re.DOTALL
                )
                if opt_match:
                    result['option_explanations'][label] = opt_match.group(1).strip()

        except Exception as e:
            logger.warning(f"Error parsing MCQ response: {e}")
            result['explanation'] = response_text.strip()

        return result

    # -------------------------------------------------------------------------
    # Topic Classification Fallback
    # -------------------------------------------------------------------------

    @staticmethod
    def classify_topic(question_text, known_topics, subject=None):
        """
        Use AI to classify a question into a topic when rule-based matching fails.

        Args:
            question_text: The question text
            known_topics: List of topic names to choose from
            subject: Subject name (optional)

        Returns:
            str | None: Topic name or None if classification fails
        """
        topics_list = ', '.join(known_topics) if known_topics else 'General'
        context = f"Subject: {subject}\n" if subject else ""

        prompt = (
            f"You are an academic topic classifier for exam questions.\n"
            f"{context}"
            f"Available topics: {topics_list}\n\n"
            f"Classify this exam question into ONE of the available topics. "
            f"If none fit well, suggest a concise topic name (max 3 words).\n"
            f"Reply with ONLY the topic name, nothing else.\n\n"
            f"Question: {question_text[:400]}"
        )

        try:
            client = get_groq_client()
            response = client.generate_response(prompt, temperature=0.1, max_tokens=15)
            topic = response.strip().strip('"').strip("'")
            logger.info(f"AI classified question to: '{topic}'")
            return topic if topic else None
        except Exception as e:
            logger.warning(f"AI topic classification failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Semantic Similarity Scanner
    # -------------------------------------------------------------------------

    @staticmethod
    def scan_for_ai_similar_groups(questions_list, subject=None):
        """
        Use AI to identify semantically similar question pairs from a list.
        Detects: same theory, same solving technique, same concept — even if
        worded differently.

        Args:
            questions_list: List of dicts with keys: id, question_text, topic_name, year
            subject: Subject name for context

        Returns:
            List of dicts: [{
                'group_label': str,       # e.g. "Stack Operations"
                'similarity_reason': str, # why they are similar
                'questions': [            # matching questions
                    {'id': int, 'text': str, 'year': int/str, 'topic': str}
                ]
            }]
        """
        if not questions_list:
            return []

        # Build numbered list for the AI
        lines = []
        for i, q in enumerate(questions_list, 1):
            year = q.get('year', '?')
            topic = q.get('topic_name', 'Unknown')
            text = q.get('question_text', '')[:150].replace('\n', ' ')
            lines.append(f"[{i}] (Year:{year}, Topic:{topic}) {text}")

        numbered_list = "\n".join(lines)
        context = f"Subject: {subject}\n" if subject else ""

        prompt = f"""You are an expert academic analyst. Analyze these exam questions and identify groups of questions that test the SAME concept, theory, or solving technique — even if the wording is different.

{context}
Questions:
{numbered_list}

Find groups where questions are semantically similar (same topic + same required knowledge/technique).
Return ONLY groups that have 2 or more questions.

Format your response EXACTLY like this (repeat for each group):
GROUP: [short descriptive label for the shared concept]
REASON: [one sentence why these questions are similar]
QUESTIONS: [comma-separated numbers from the list, e.g. 1, 3, 7]
---

If no similar groups exist, reply with: NO_GROUPS"""

        try:
            client = get_groq_client()
            response = client.generate_response(prompt, temperature=0.2, max_tokens=800)
            return QuestionAssistant._parse_similarity_response(response, questions_list)
        except Exception as e:
            logger.error(f"AI similarity scan failed: {e}")
            return []

    @staticmethod
    def _parse_similarity_response(response_text, questions_list):
        """Parse the AI similarity scanner response into structured groups."""
        import re

        if 'NO_GROUPS' in response_text:
            return []

        groups = []
        # Split by the --- separator
        blocks = re.split(r'\n---\n?', response_text)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            group_match = re.search(r'GROUP:\s*(.+)', block)
            reason_match = re.search(r'REASON:\s*(.+)', block)
            questions_match = re.search(r'QUESTIONS:\s*(.+)', block)

            if not (group_match and questions_match):
                continue

            label = group_match.group(1).strip()
            reason = reason_match.group(1).strip() if reason_match else ''
            q_nums_str = questions_match.group(1).strip()

            # Parse question indices (1-based)
            q_indices = []
            for num_str in re.split(r'[,\s]+', q_nums_str):
                try:
                    idx = int(num_str.strip()) - 1  # Convert to 0-based
                    if 0 <= idx < len(questions_list):
                        q_indices.append(idx)
                except ValueError:
                    continue

            if len(q_indices) < 2:
                continue

            matched_questions = []
            for idx in q_indices:
                q = questions_list[idx]
                matched_questions.append({
                    'id': q.get('id'),
                    'text': q.get('question_text', ''),
                    'year': q.get('year', '?'),
                    'topic': q.get('topic_name', 'Unknown'),
                    'type': q.get('question_type', 'Unknown'),
                })

            groups.append({
                'group_label': label,
                'similarity_reason': reason,
                'questions': matched_questions,
            })

        return groups
