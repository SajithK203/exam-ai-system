-- Insert sample questions for testing the dashboard

-- Get topic IDs for reference
SET @ds_id = (SELECT id FROM topics WHERE topic_name = 'Data Structures' LIMIT 1);
SET @algo_id = (SELECT id FROM topics WHERE topic_name = 'Algorithms' LIMIT 1);
SET @oop_id = (SELECT id FROM topics WHERE topic_name = 'Object-Oriented Programming' LIMIT 1);
SET @db_id = (SELECT id FROM topics WHERE topic_name = 'Database Design' LIMIT 1);
SET @net_id = (SELECT id FROM topics WHERE topic_name = 'Network Protocols' LIMIT 1);
SET @os_id = (SELECT id FROM topics WHERE topic_name = 'Operating Systems' LIMIT 1);
SET @se_id = (SELECT id FROM topics WHERE topic_name = 'Software Engineering' LIMIT 1);

-- Paper 1 (2021) - 5 questions
INSERT INTO questions (paper_id, question_text, topic_id, question_type, marks_allocated, difficulty_level) 
VALUES 
(1, 'What is a data structure? Explain with examples.', @ds_id, 'Long Answer', 5, 'Easy'),
(1, 'Define normalization in database design.', @db_id, 'Short Answer', 3, 'Easy'),
(1, 'Implement a stack using arrays. Explain push and pop operations.', @ds_id, 'Practical', 8, 'Medium'),
(1, 'Which sorting algorithm is most efficient? A) Quicksort  B) Mergesort  C) Bubblesort  D) Heapsort', @algo_id, 'Multiple Choice', 2, 'Easy'),
(1, 'Discuss the role of inheritance in OOP design.', @oop_id, 'Long Answer', 6, 'Medium');

-- Paper 4 (2019) - 5 questions
INSERT INTO questions (paper_id, question_text, topic_id, question_type, marks_allocated, difficulty_level)
VALUES
(4, 'What is a primary key?', @db_id, 'Short Answer', 2, 'Easy'),
(4, 'Explain the difference between TCP and UDP protocols.', @net_id, 'Long Answer', 7, 'Hard'),
(4, 'Design a database schema for an e-commerce system.', @db_id, 'Practical', 10, 'Hard'),
(4, 'Name three data structures and their applications.', @ds_id, 'Short Answer', 4, 'Medium'),
(4, 'What are ACID properties in databases?', @db_id, 'Long Answer', 8, 'Medium');

-- Paper 5 (2018) - 4 questions
INSERT INTO questions (paper_id, question_text, topic_id, question_type, marks_allocated, difficulty_level)
VALUES
(5, 'What is a thread? How does it differ from a process?', @os_id, 'Long Answer', 5, 'Medium'),
(5, 'List three design patterns used in software development.', @se_id, 'Short Answer', 3, 'Easy'),
(5, 'Explain the concept of polymorphism in OOP.', @oop_id, 'Long Answer', 6, 'Medium'),
(5, 'What is cache memory? Explain its role in system performance.', @os_id, 'Short Answer', 3, 'Easy');

-- Paper 6 (2017) - 6 questions
INSERT INTO questions (paper_id, question_text, topic_id, question_type, marks_allocated, difficulty_level)
VALUES
(6, 'Define Big O notation and give examples.', @algo_id, 'Long Answer', 7, 'Hard'),
(6, 'What is a linked list? Implement insertion.', @ds_id, 'Practical', 9, 'Hard'),
(6, 'Differentiate between SQL and NoSQL databases.', @db_id, 'Long Answer', 8, 'Medium'),
(6, 'Explain the concept of encapsulation.', @oop_id, 'Short Answer', 4, 'Easy'),
(6, 'Design and implement a binary search tree.', @ds_id, 'Practical', 10, 'Hard'),
(6, 'What are microservices? Discuss their advantages.', @se_id, 'Long Answer', 7, 'Medium');

-- Update paper with question counts
UPDATE papers SET total_questions = 5, is_processed = 1 WHERE id = 1;
UPDATE papers SET total_questions = 5, is_processed = 1 WHERE id = 4;
UPDATE papers SET total_questions = 4, is_processed = 1 WHERE id = 5;
UPDATE papers SET total_questions = 6, is_processed = 1 WHERE id = 6;
