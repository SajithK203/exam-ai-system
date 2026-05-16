-- =============================================================
-- v2 Migration: Question Bank Enhancements
-- Run once against exam_analysis_system database
-- Safe to run multiple times (uses IF NOT EXISTS / IGNORE)
-- =============================================================

USE exam_analysis_system;

-- 1. Add file_hash column to papers for duplicate detection
ALTER TABLE papers 
    ADD COLUMN IF NOT EXISTS file_hash VARCHAR(32) DEFAULT NULL,
    ADD INDEX IF NOT EXISTS idx_file_hash (file_hash);

-- 2. Add AI classification tracking columns to questions
ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS ai_classified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS topic_confidence FLOAT DEFAULT 0.0;

-- 3. Make sure question_options table exists (was in v1 schema but ensure it's present)
CREATE TABLE IF NOT EXISTS question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    option_label VARCHAR(10),
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_question_id (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Done
SELECT 'v2 migration complete' AS status;
