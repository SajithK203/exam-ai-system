# Database Schema Documentation

## Overview

The system uses MySQL with 9 core tables and optimized indexing for exam paper analysis.

## Tables

### 1. papers
Stores metadata about uploaded exam papers.

```sql
- id: Primary key
- subject: Subject name (indexed)
- exam_title: Title of the exam
- year: Exam year (indexed)
- exam_type: Midterm/Final/Quiz/Practice
- file_path: Path to uploaded PDF (unique)
- file_size: Size in bytes
- total_questions: Count of questions
- upload_date: Timestamp
- is_processed: Boolean flag
```

### 2. questions
Stores extracted questions from papers.

```sql
- id: Primary key
- paper_id: Foreign key to papers (indexed)
- question_text: Full question text (full-text indexed)
- topic_id: Foreign key to topics (indexed)
- question_type: MCQ/Short/Long/Practical
- marks_allocated: Marks for the question
- frequency: How many times appeared
- difficulty_level: Easy/Medium/Hard
- created_at: Timestamp
```

### 3. topics
Question topic categories.

```sql
- id: Primary key
- topic_name: Unique topic name (indexed)
- category: General category
- description: Topic description
```

### 4. question_options
MCQ options for multiple choice questions.

```sql
- id: Primary key
- question_id: Foreign key to questions (indexed)
- option_text: Option content
- option_label: A, B, C, D
- is_correct: Boolean flag
```

### 5. question_patterns
Pre-computed analytics data.

```sql
- subject: Subject name (indexed)
- topic_id: Foreign key (indexed)
- year: Year (indexed)
- frequency: Number of questions
- trend_direction: Increasing/Decreasing/Stable
```

### 6. mock_exams
Generated practice exams.

```sql
- id: Primary key
- exam_name: Name of mock exam
- subject: Subject name (indexed)
- total_questions: Count
- total_marks: Total marks
```

### 7. mock_exam_questions
Links questions to mock exams (many-to-many).

```sql
- mock_exam_id: Foreign key (indexed)
- question_id: Foreign key
- question_order: Order in exam
- marks: Marks for this question
```

### 8. ai_insights
Cached AI-generated insights.

```sql
- subject: Subject name (indexed)
- insight_type: Type of insight
- insight_text: Generated text
- generated_at: Timestamp (indexed)
```

### 9. processing_logs
Audit trail of data processing.

```sql
- paper_id: Foreign key (indexed)
- processing_stage: Stage of processing
- status: Success/Failed/In Progress
- message: Log message
```

## Indexing Strategy

**Single Column Indexes:**
- papers.subject
- papers.year
- questions.paper_id
- questions.topic_id
- topics.topic_name
- mock_exams.subject

**Full-Text Index:**
- questions.question_text (for full-text search)

**Composite Indexes:**
- question_patterns(subject, year)
- mock_exam_questions(mock_exam_id, question_id)

## Relationships

```
papers (1) ──── (M) questions
papers (1) ──── (M) processing_logs

questions (M) ──── (1) topics
questions (1) ──── (M) question_options
questions (M) ──── (M) mock_exams (via mock_exam_questions)

topics (1) ──── (M) question_patterns
```

## Query Patterns

### Frequently Used Queries

**Get topic frequency:**
```sql
SELECT topic_id, COUNT(*) as frequency
FROM questions
WHERE paper_id IN (SELECT id FROM papers WHERE subject = ?)
GROUP BY topic_id
ORDER BY frequency DESC
```

**Search questions:**
```sql
SELECT * FROM questions
WHERE MATCH(question_text) AGAINST(? IN BOOLEAN MODE)
```

**Get trending topics:**
```sql
SELECT year, topic_id, COUNT(*) as frequency
FROM questions q
JOIN papers p ON q.paper_id = p.id
GROUP BY year, topic_id
ORDER BY year DESC, frequency DESC
```

## Performance Optimization Tips

1. **Use EXPLAIN**: Test query plans
2. **Pagination**: Use LIMIT/OFFSET for large results
3. **Connection Pooling**: Reuse connections
4. **Batch Inserts**: Insert multiple rows at once
5. **Archive Old Data**: Move old papers to archive table

## Maintenance

### Regular Tasks

- Analyze tables monthly: `ANALYZE TABLE papers, questions;`
- Optimize tables quarterly: `OPTIMIZE TABLE papers, questions;`
- Check indexes: `CHECK TABLE papers, questions;`
- Backup daily: `mysqldump -u user -p database > backup.sql`

### Monitoring

Monitor these metrics:
- Query execution time
- Index usage (slow query log)
- Table fragmentation
- Connection pool utilization
