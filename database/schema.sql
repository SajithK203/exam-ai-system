-- MySQL Database Schema for AI Exam Paper Analysis System
-- Create database
CREATE DATABASE IF NOT EXISTS exam_analysis_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE exam_analysis_system;

-- Table 1: Papers (uploaded exam papers)
CREATE TABLE IF NOT EXISTS papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    exam_title VARCHAR(255),
    year INT,
    exam_type ENUM('Midterm', 'Final', 'Quiz', 'Practice') DEFAULT 'Final',
    file_path VARCHAR(500) NOT NULL UNIQUE,
    file_size INT,
    file_hash VARCHAR(64) DEFAULT NULL,
    total_questions INT DEFAULT 0,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    INDEX idx_subject (subject),
    INDEX idx_year (year),
    INDEX idx_exam_type (exam_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: Topics (category of questions)
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_topic_name (topic_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 3: Questions (extracted from papers)
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    question_text LONGTEXT NOT NULL,
    topic_id INT,
    question_type ENUM('Multiple Choice', 'Short Answer', 'Long Answer', 'Practical') DEFAULT 'Long Answer',
    marks_allocated INT DEFAULT 0,
    frequency INT DEFAULT 1,
    difficulty_level ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    extraction_confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    INDEX idx_paper_id (paper_id),
    INDEX idx_topic_id (topic_id),
    INDEX idx_question_type (question_type),
    FULLTEXT INDEX ft_question_text (question_text)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 4: Question Options (for MCQ type questions)
CREATE TABLE IF NOT EXISTS question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    option_label VARCHAR(10),
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_question_id (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 5: Question Patterns (analytics data)
CREATE TABLE IF NOT EXISTS question_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    topic_id INT,
    year INT,
    frequency INT DEFAULT 1,
    total_appearances INT DEFAULT 0,
    avg_marks FLOAT DEFAULT 0,
    trend_direction ENUM('Increasing', 'Decreasing', 'Stable') DEFAULT 'Stable',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    UNIQUE KEY unique_pattern (subject, topic_id, year),
    INDEX idx_subject (subject),
    INDEX idx_year (year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 6: Mock Exams (generated practice exams)
CREATE TABLE IF NOT EXISTS mock_exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    total_questions INT NOT NULL,
    total_marks INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_subject (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 7: Mock Exam Questions (many-to-many relationship)
CREATE TABLE IF NOT EXISTS mock_exam_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mock_exam_id INT NOT NULL,
    question_id INT NOT NULL,
    question_order INT NOT NULL,
    marks INT DEFAULT 0,
    FOREIGN KEY (mock_exam_id) REFERENCES mock_exams(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_mock_question (mock_exam_id, question_id),
    INDEX idx_mock_exam_id (mock_exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 8: AI Insights Cache (store generated recommendations)
CREATE TABLE IF NOT EXISTS ai_insights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    insight_type ENUM('Study Recommendation', 'Topic Focus', 'Trend Analysis', 'Mock Suggestion') DEFAULT 'Study Recommendation',
    insight_text LONGTEXT NOT NULL,
    topics_involved JSON,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_model VARCHAR(100),
    ttl_hours INT DEFAULT 24,
    is_expired BOOLEAN DEFAULT FALSE,
    INDEX idx_subject (subject),
    INDEX idx_generated_at (generated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 9: Processing Logs (audit trail)
CREATE TABLE IF NOT EXISTS processing_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT,
    processing_stage ENUM('Upload', 'Extraction', 'Parsing', 'Classification', 'Storage', 'Complete', 'Error') DEFAULT 'Upload',
    status ENUM('Success', 'Failed', 'In Progress') DEFAULT 'In Progress',
    message TEXT,
    details JSON,
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE SET NULL,
    INDEX idx_paper_id (paper_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Initial topic data (sample)
INSERT IGNORE INTO topics (topic_name, category, description) VALUES
('Binary Trees', 'Data Structures', 'Tree-based data structure with at most two children per node'),
('Linked Lists', 'Data Structures', 'Linear data structure with nodes pointing to next element'),
('Graphs', 'Data Structures', 'Non-linear data structure with vertices and edges'),
('Sorting Algorithms', 'Algorithms', 'Techniques to arrange elements in specific order'),
('Searching Algorithms', 'Algorithms', 'Techniques to find elements in data structure'),
('Dynamic Programming', 'Algorithms', 'Optimization technique using memoization and tabulation'),
('Hash Tables', 'Data Structures', 'Key-value pair storage with hash function'),
('Stacks & Queues', 'Data Structures', 'Linear data structures with LIFO and FIFO principles'),
('String Manipulation', 'Algorithms', 'Operations on string data'),
('Database Design', 'Database', 'Design and normalization of databases');
