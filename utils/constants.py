"""
Constants - Global constants and configuration values.
"""

# Application Constants
APP_TITLE = "AI Exam Analysis System"
APP_VERSION = "1.0.0"

# Question Types
QUESTION_TYPES = [
    "Multiple Choice",
    "Short Answer",
    "Long Answer",
    "Practical"
]

# Difficulty Levels
DIFFICULTY_LEVELS = [
    "Easy",
    "Medium",
    "Hard"
]

# Exam Types
EXAM_TYPES = [
    "Midterm",
    "Final",
    "Quiz",
    "Practice"
]

# Common Topics
DEFAULT_TOPICS = [
    "Binary Trees",
    "Linked Lists",
    "Graphs",
    "Sorting Algorithms",
    "Searching Algorithms",
    "Dynamic Programming",
    "Hash Tables",
    "Stacks & Queues",
    "String Manipulation",
    "Database Design"
]

# Time Constants (in seconds)
PDF_EXTRACTION_TIMEOUT = 30
DATABASE_QUERY_TIMEOUT = 5
API_REQUEST_TIMEOUT = 30

# Size Limits
MAX_PDF_SIZE_MB = 50
MAX_QUESTION_LENGTH = 10000
MIN_QUESTION_LENGTH = 20

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Colors for UI
COLOR_PRIMARY = "#1f77b4"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#ff7f0e"
COLOR_ERROR = "#d62728"

# Date Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 3600  # 1 hour
CACHE_TTL_LONG = 86400  # 1 day

# AI Model Settings
DEFAULT_AI_MODEL = "llama-3-70b-versatile"
DEFAULT_AI_TEMPERATURE = 0.7
DEFAULT_AI_MAX_TOKENS = 1000

# Database
DEFAULT_DB_POOL_SIZE = 5
MAX_DB_POOL_CONNECTIONS = 20
DB_QUERY_RETRY_COUNT = 3
DB_QUERY_RETRY_DELAY = 1  # seconds

# Regex Patterns
QUESTION_NUMBER_PATTERN = r'^(?:Q|Question)\s*\.?\s*(\d+)'
MCQ_OPTION_PATTERN = r'^\s*([A-D])\s*[\)\.:\-]\s*(.+)'
MARKS_PATTERN = r'(?:\(|\[)?\s*(\d+)\s*(?:[Mm]arks?)?(?:\)|\])?'
