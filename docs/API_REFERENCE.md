# API Reference

## Backend API Modules

### pdf_processor.py

```python
PDFProcessor.extract_text_from_pdf(file_path, timeout=None)
  # Extract text from PDF file
  # Returns: str (extracted text)
  
PDFProcessor.get_pdf_metadata(file_path)
  # Get PDF metadata
  # Returns: dict {file_name, file_size, pages, title, author}
  
PDFProcessor.validate_pdf(file_path)
  # Validate if file is valid PDF
  # Returns: bool
```

### text_cleaner.py

```python
TextCleaner.clean_text(text)
  # Basic text cleaning
  # Returns: str (cleaned text)

TextCleaner.full_clean(text)
  # Complete cleaning pipeline
  # Returns: str (fully cleaned text)

TextCleaner.normalize_whitespace(text)
  # Normalize spaces and newlines
  # Returns: str

TextCleaner.remove_special_characters(text, keep_chars=None)
  # Remove special characters
  # Returns: str
```

### question_extractor.py

```python
QuestionExtractor.extract_questions(text, min_length=None)
  # Extract questions from text
  # Returns: list[str]

QuestionExtractor.identify_question_type(question_text)
  # Identify question type
  # Returns: str ('Multiple Choice' | 'Short Answer' | 'Long Answer' | 'Practical')

QuestionExtractor.extract_options(question_text)
  # Extract MCQ options
  # Returns: list[dict] [{label, text}]

QuestionExtractor.estimate_marks(question_text)
  # Estimate marks for question
  # Returns: int

QuestionExtractor.parse_question_full(question_text)
  # Complete question parsing
  # Returns: dict {text, type, options, marks, word_count}
```

### topic_classifier.py

```python
TopicClassifier.classify_question(question_text)
  # Classify question to topic
  # Returns: str (topic_name) | None

TopicClassifier.classify_batch(questions_list)
  # Classify multiple questions
  # Returns: list[dict] [{question, topic, confidence}]

TopicClassifier.suggest_topics(question_text, top_n=3)
  # Suggest top N topics
  # Returns: list[tuple] [(topic, score), ...]

TopicClassifier.get_topic_id_by_name(topic_name)
  # Get topic ID from database
  # Returns: int | None

TopicClassifier.create_missing_topic(topic_name)
  # Create topic if not exists
  # Returns: int (topic_id)
```

### analytics_engine.py

```python
AnalyticsEngine.get_full_analysis(subject, years=None)
  # Get comprehensive analysis
  # Returns: dict {topic_frequency, trends, question_types, ...}

AnalyticsEngine.get_study_focus_areas(subject, top_n=5)
  # Get top focus areas
  # Returns: list[dict] [{topic_name, frequency}]

AnalyticsEngine.get_trend_analysis(subject, topic_id, years=10)
  # Get topic trends over years
  # Returns: list[dict] [{year, frequency, marks}]
```

## Database Query APIs

### paper_queries.py

```python
PaperQueries.create_paper(subject, exam_title, year, exam_type, file_path, file_size)
  # Create new paper
  # Returns: bool

PaperQueries.get_paper_by_id(paper_id)
  # Get paper details
  # Returns: dict

PaperQueries.get_papers_by_subject(subject)
  # Get all papers for subject
  # Returns: list[dict]

PaperQueries.get_unique_subjects()
  # Get all unique subjects
  # Returns: list[str]

PaperQueries.get_unique_years()
  # Get all unique years
  # Returns: list[int]

PaperQueries.update_paper_status(paper_id, is_processed, total_questions=None)
  # Update paper status
  # Returns: bool
```

### question_queries.py

```python
QuestionQueries.create_question(paper_id, question_text, topic_id, question_type, marks=0)
  # Create new question
  # Returns: bool

QuestionQueries.get_questions_by_paper(paper_id)
  # Get questions for paper
  # Returns: list[dict]

QuestionQueries.get_questions_by_topic(topic_id, limit=None)
  # Get questions for topic
  # Returns: list[dict]

QuestionQueries.search_questions(search_text)
  # Full-text search questions
  # Returns: list[dict]

QuestionQueries.get_repeated_questions()
  # Find questions appearing multiple times
  # Returns: list[dict]
```

### analytics_queries.py

```python
AnalyticsQueries.get_topic_frequency(subject=None, years=None)
  # Get topic frequency distribution
  # Returns: list[dict] [{topic_name, frequency}]

AnalyticsQueries.get_trending_topics(subject, years=5)
  # Get topics over years
  # Returns: list[dict] [{topic_name, year, frequency}]

AnalyticsQueries.get_top_topics(subject, limit=10)
  # Get top N topics
  # Returns: list[dict]

AnalyticsQueries.get_question_type_distribution(subject=None)
  # Get question type distribution
  # Returns: list[dict] [{question_type, count, percentage}]

AnalyticsQueries.get_difficulty_distribution(subject=None)
  # Get difficulty distribution
  # Returns: list[dict] [{difficulty_level, count}]

AnalyticsQueries.get_subject_statistics()
  # Get statistics for all subjects
  # Returns: list[dict]
```

## AI Integration APIs

### groq_client.py

```python
groq = GroqClient()
  # Initialize Groq client

groq.generate_response(prompt, temperature=None, max_tokens=None)
  # Generate AI response
  # Returns: str

groq.generate_study_recommendation(subject, topics_data)
  # Generate study recommendation
  # Returns: str

groq.test_connection()
  # Test API connection
  # Returns: bool

get_groq_client()
  # Get singleton Groq client instance
  # Returns: GroqClient
```

### recommendation_engine.py

```python
RecommendationEngine.generate_study_plan(subject)
  # Generate comprehensive study plan
  # Returns: dict {subject, top_topics, ai_recommendation, generated_at}

RecommendationEngine.generate_mock_exam_suggestions(subject)
  # Generate mock exam suggestions
  # Returns: dict {subject, suggestions, recommended_topics}

RecommendationEngine.generate_topic_focus_guide(subject, topic_name)
  # Generate topic focus guide
  # Returns: dict {subject, topic, frequency, guide}

RecommendationEngine.generate_weak_area_analysis(subject)
  # Identify weak areas
  # Returns: dict {subject, analysis, generated_at}

RecommendationEngine.generate_time_management_plan(subject)
  # Generate time management strategy
  # Returns: dict {subject, strategy, exam_stats}
```

## Frontend Components

### session_state.py

```python
SessionManager.initialize_session()
  # Initialize all session variables

SessionManager.set_current_subject(subject)
SessionManager.get_current_subject()
  # Manage current subject

SessionManager.cache_analysis(subject, data)
SessionManager.get_cached_analysis(subject)
  # Cache analysis results

SessionManager.set_mock_exam(exam_data)
SessionManager.get_mock_exam()
  # Manage mock exam
```

### formatters.py

```python
DataFormatters.format_question(question)
  # Format question for display

DataFormatters.format_topic_frequency(topics)
  # Format topic data

DataFormatters.format_paper_info(paper)
  # Format paper metadata

DataFormatters.format_file_size(size_bytes)
  # Format file size (B, KB, MB, etc.)

DataFormatters.format_percentage(value, total)
  # Format as percentage

DataFormatters.truncate_text(text, max_length=100)
  # Truncate long text
```

## Error Codes

| Code | Message | Action |
|------|---------|--------|
| E001 | PDF not found | Check file path |
| E002 | Invalid PDF | Verify PDF integrity |
| E003 | Database connection error | Check DB config |
| E004 | API key invalid | Verify GROQ_API_KEY |
| E005 | File too large | Upload smaller file |
| E006 | Text extraction failed | Try different PDF |
| E007 | Classification failed | Manual topic entry |

## Rate Limiting

- Groq API: Default limits apply
- Database: Connection pool of 5-20
- File uploads: 50MB max
- Search queries: 1000 results max

## Caching

| Resource | TTL | Strategy |
|----------|-----|----------|
| Topic frequency | 1 hour | Memory |
| Analysis results | 24 hours | Memory |
| PDF metadata | Session | Memory |
| AI responses | 24 hours | Database |
