"""
Configuration settings for the exam analysis system.
Centralized configuration management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "exam_analysis_system"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "autocommit": True,
    "use_unicode": True,
    "charset": "utf8mb4"
}

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, os.getenv("UPLOAD_FOLDER", "uploads"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50000000))  # 50MB
ALLOWED_EXTENSIONS = {"pdf"}

# Logging Configuration
LOG_FOLDER = os.path.join(PROJECT_ROOT, "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application Configuration
APP_NAME = os.getenv("PROJECT_NAME", "AI Exam Analysis System")
APP_VERSION = os.getenv("PROJECT_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# PDF Processing Configuration
PDF_CONFIG = {
    "extract_text_timeout": 30,
    "min_question_length": 20,  # Minimum characters for a valid question
}

# Question Classification Configuration
QUESTION_CONFIG = {
    "types": ["Multiple Choice", "Short Answer", "Long Answer", "Practical"],
    "default_type": "Long Answer"
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    "top_topics_limit": 10,
    "trend_years": 5,
}

# AI Configuration
AI_CONFIG = {
    "model": "llama-3.3-70b-versatile",  # Updated from deprecated llama-3-70b-versatile
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1
}

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
