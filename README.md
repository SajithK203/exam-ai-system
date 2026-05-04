# 📚 AI Exam Paper Analysis & Smart Study Recommendation System

## 🎯 Project Overview

This intelligent system analyzes past exam papers to provide data-driven study recommendations using AI. It combines data engineering, database design, and machine learning to help students prepare effectively for exams.

### 🌟 Key Features

- 📄 **Automatic Question Extraction**: Upload PDF exam papers and automatically extract questions
- 📊 **Pattern Analysis**: Identify most frequently asked topics and trends
- 🤖 **AI Recommendations**: Get personalized study guidance powered by Groq AI
- ❓ **Question Bank**: Searchable repository of all extracted questions
- 📝 **Mock Exam Generator**: Create practice exams based on historical patterns
- 📈 **Analytics Dashboard**: Visual insights into exam patterns and difficulty

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                      │
│  (Upload | Analysis | Questions | Insights | Mock Exam)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend Services                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   PDF    │  │   Text   │  │Question  │  │  Topic   │   │
│  │Processor │─▶│ Cleaner  │─▶│Extractor │─▶│Classifier│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                      │                      │
│  ┌─────────────────────────────────▼──────────────┐        │
│  │  MySQL Database (Structured Storage)           │        │
│  │  ┌────────┐ ┌──────────┐ ┌────────────────┐   │        │
│  │  │ Papers │ │Questions │ │ Analytics     │   │        │
│  │  └────────┘ └──────────┘ └────────────────┘   │        │
│  └─────────────────────────────────┬──────────────┘        │
│                                      │                      │
│  ┌─────────────────────────────────▼──────────────┐        │
│  │  Analytics Engine & AI Integration              │        │
│  │  ┌──────────────┐  ┌──────────────────────┐   │        │
│  │  │   SQL        │  │  Groq AI RAG Layer   │   │        │
│  │  │  Analytics   │─▶│  (Recommendations)   │   │        │
│  │  └──────────────┘  └──────────────────────┘   │        │
│  └──────────────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- Groq API Key
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   cd "AI-Based Exam Paper Analysis & Smart Study Recommendation System"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

6. **Run the application**
   ```bash
   streamlit run frontend/app.py
   ```

The application will start at `http://localhost:8501`

## 📋 Project Structure

```
project-root/
├── config/                 # Configuration & settings
├── database/              # Database layer (MySQL)
│   ├── schema.sql        # Database schema
│   ├── connection.py     # Connection pooling
│   └── queries/          # CRUD & analytics queries
├── modules/              # Processing pipeline
│   ├── pdf_processor.py   # PDF text extraction
│   ├── text_cleaner.py    # Text preprocessing
│   ├── question_extractor.py  # Question parsing
│   ├── topic_classifier.py    # Topic identification
│   └── analytics_engine.py    # Statistical analysis
├── ai/                   # AI & RAG integration
│   ├── groq_client.py    # Groq API client
│   ├── prompts.py        # AI prompt templates
│   └── recommendation_engine.py  # Study recommendations
├── frontend/             # Streamlit UI
│   ├── app.py           # Main entry point
│   └── pages/           # Page modules (upload, analysis, etc.)
├── utils/               # Utility modules
├── tests/               # Test suite
└── requirements.txt     # Python dependencies
```

## 🔄 Data Flow

1. **Upload** → User uploads exam PDF
2. **Extract** → System extracts text using PyPDF2
3. **Clean** → Text preprocessing and normalization
4. **Parse** → Questions identified using regex
5. **Classify** → Topics assigned using rule-based approach
6. **Store** → Data persisted in MySQL
7. **Analyze** → SQL queries generate insights
8. **Recommend** → AI generates study recommendations
9. **Display** → Results shown in Streamlit dashboard

## 💾 Database Schema

### Key Tables

- **papers**: Exam papers metadata
- **questions**: Extracted questions with classification
- **topics**: Subject topic categories
- **question_patterns**: Frequency & trend analytics
- **mock_exams**: Generated practice exams
- **ai_insights**: Cached AI-generated insights

## 🤖 AI Integration (RAG)

The system uses **Retrieval-Augmented Generation (RAG)**:

1. **Retrieval**: Fetch questions and statistics from MySQL
2. **Generation**: Send context to Groq AI for personalized insights
3. **Output**: Actionable recommendations for students

Example flow:
```
Topics: Trees (15x), Graphs (8x)
        ↓
     [Groq AI]
        ↓
"Focus on Trees, especially traversal and balancing..."
```

## 📊 Sample Analytics

- **Topic Frequency**: Shows most asked topics
- **Question Type Distribution**: MCQ vs Long Answer breakdown
- **Difficulty Progression**: Easy/Medium/Hard distribution
- **Year-over-Year Trends**: Topic popularity over time
- **Repeated Questions**: Questions appearing in multiple papers

## 🧪 API Examples

### Extract questions from PDF
```python
from modules.pdf_processor import PDFProcessor
from modules.text_cleaner import TextCleaner
from modules.question_extractor import QuestionExtractor

pdf_processor = PDFProcessor()
text = pdf_processor.extract_text_from_pdf("exam.pdf")

cleaner = TextCleaner()
cleaned = cleaner.full_clean(text)

extractor = QuestionExtractor()
questions = extractor.extract_questions(cleaned)
```

### Get topic frequency
```python
from database.queries.analytics_queries import AnalyticsQueries

frequency = AnalyticsQueries.get_topic_frequency("Computer Science")
```

### Generate AI recommendations
```python
from ai.recommendation_engine import RecommendationEngine

plan = RecommendationEngine.generate_study_plan("Computer Science")
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=exam_analysis_system

GROQ_API_KEY=your_groq_api_key

UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=50000000

DEBUG=False
LOG_LEVEL=INFO
```

## 📈 Performance Optimization

- Connection pooling for MySQL
- Caching of frequently accessed data
- Indexed database queries
- Batch processing of questions
- Asynchronous file operations

## 🧪 Testing

Run tests:
```bash
pytest tests/ -v
```

## 🐛 Troubleshooting

### Database connection error
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database schema is initialized

### PDF processing fails
- Verify PDF file is valid (not corrupted)
- Check file size is under 50MB
- Ensure file has readable text (not scanned images)

### AI API errors
- Verify Groq API key is valid
- Check internet connectivity
- Verify API rate limits not exceeded

## 📚 Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Reference](docs/API_REFERENCE.md)
- [User Guide](docs/USER_GUIDE.md)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Push to branch
5. Create pull request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Author

AI Exam Analysis System Development Team

## 🙏 Acknowledgments

- Streamlit for UI framework
- Groq for AI services
- MySQL for database
- PyPDF2 for PDF processing

## 📞 Support

For issues and questions:
- Create GitHub issue
- Email: support@examanalysis.com
- Documentation: Check `/docs` folder

---

**Last Updated**: May 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
