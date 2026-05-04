# System Architecture

## High-Level Overview

The AI Exam Analysis System is built with a clean separation of concerns:

### **Layer 1: Frontend (Presentation)**
- Streamlit-based web interface
- 5 main pages: Upload, Analysis, Questions, Insights, Mock Exam
- Real-time data visualization with Plotly
- Session state management for user interactions

### **Layer 2: Backend (Application Logic)**
- PDF processing and text extraction
- Question parsing and classification
- Analytics computation
- AI integration and prompt management

### **Layer 3: Data Layer**
- MySQL database for structured storage
- Connection pooling for performance
- Optimized queries with proper indexing
- Transaction management

### **Layer 4: External Services**
- Groq API for AI-powered insights
- RAG (Retrieval-Augmented Generation) pipeline

## Data Processing Pipeline

```
PDF Upload
    │
    ├─▶ PDFProcessor.extract_text()
    │   └─▶ Raw text extracted
    │
    ├─▶ TextCleaner.full_clean()
    │   └─▶ Normalized, cleaned text
    │
    ├─▶ QuestionExtractor.extract_questions()
    │   └─▶ Individual questions identified
    │
    ├─▶ QuestionExtractor.identify_question_type()
    │   └─▶ MCQ / Short Answer / Long Answer
    │
    ├─▶ TopicClassifier.classify_question()
    │   └─▶ Topic assigned (using keyword matching)
    │
    ├─▶ Database storage
    │   └─▶ Papers and Questions tables updated
    │
    └─▶ Analytics Engine
        └─▶ Frequency analysis computed
```

## Module Responsibilities

### **config/**
- `settings.py`: Central configuration management
- `logging_config.py`: Application-wide logging setup
- `database.py`: MySQL connection configuration

### **database/**
- `connection.py`: Connection pooling and query execution
- `schema.sql`: MySQL table definitions
- `queries/`: CRUD and analytics operations
  - `paper_queries.py`: Paper management
  - `question_queries.py`: Question operations
  - `analytics_queries.py`: Statistical queries

### **modules/**
- `pdf_processor.py`: PyPDF2-based PDF extraction
- `text_cleaner.py`: Text preprocessing and normalization
- `question_extractor.py`: Question parsing with regex
- `topic_classifier.py`: Rule-based topic classification
- `analytics_engine.py`: High-level analytics interface

### **ai/**
- `groq_client.py`: Groq API integration
- `prompts.py`: Prompt templates for different insights
- `recommendation_engine.py`: Study recommendation generation

### **frontend/**
- `app.py`: Main Streamlit application
- `pages/`: Individual page implementations
- `components/`: Reusable UI components
- `utils/`: Session management and formatters

### **utils/**
- `file_handler.py`: File upload/download operations
- `validators.py`: Input validation
- `logger.py`: Logging configuration
- `constants.py`: Application-wide constants

## Database Design

### Schema Relationships

```
papers (1)
  └─── (M) questions
       └─── (1) topics
       
mock_exams (1)
  └─── (M) mock_exam_questions
       └─── (1) questions

question_patterns ─── topics
ai_insights ─── subjects
processing_logs ─── papers
```

### Key Optimizations

- Full-text index on `questions.question_text`
- Indexed foreign keys for join performance
- Separate analytics table for pre-computed results
- Proper normalization to avoid data redundancy

## API Design

### REST-like Query Pattern

```python
# Get operations
papers = PaperQueries.get_papers_by_subject("CS")
questions = QuestionQueries.get_questions_by_topic(topic_id)
frequency = AnalyticsQueries.get_topic_frequency("CS")

# Modify operations
PaperQueries.create_paper(...)
QuestionQueries.update_question_topic(...)

# Analysis operations
trends = AnalyticsQueries.get_trending_topics("CS", years=5)
stats = AnalyticsQueries.get_subject_statistics()
```

## RAG Pipeline

### Workflow

1. **User Action**: Student requests study recommendations
2. **Retrieval**: System fetches:
   - Top topics from database
   - Real questions on those topics
   - Frequency statistics
3. **Augmentation**: Data formatted into context
4. **Generation**: Sent to Groq API with domain-specific prompt
5. **Output**: AI response delivered to user

### Example

```
Input: "Computer Science" subject
  ↓
Retrieved: Trees (15), Graphs (8), DP (6)
  ↓
Prompt: "Based on this data, what should CS students focus on?"
  ↓
Output: "Focus on Trees, especially AVL balancing. Trees appear in 50% of exams..."
```

## Performance Considerations

### Caching Strategy
- Session-level caching for analysis results
- Database query result caching
- AI response caching (24-hour TTL)

### Database Optimization
- Connection pooling (5-20 connections)
- Query optimization with indexes
- Batch operations for bulk inserts
- Pagination for large result sets

### Frontend Optimization
- Lazy loading of data
- Streamlit's native caching
- Efficient chart rendering with Plotly
- Session state management

## Security

### Input Validation
- File type validation
- File size limits (50MB max)
- SQL injection prevention via parameterized queries
- XSS prevention through Streamlit

### Authentication (Future)
- User accounts and sessions
- Role-based access control
- Audit logging

## Error Handling Strategy

- Try-catch blocks at module boundaries
- Logging of all errors with context
- User-friendly error messages
- Graceful degradation

## Scalability Considerations

### Current Limitations
- Single MySQL instance
- Synchronous processing
- In-memory session state

### Future Improvements
- Database replication/sharding
- Asynchronous task queue
- Distributed caching (Redis)
- Microservices architecture
