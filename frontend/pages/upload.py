"""
Upload Page - Handle PDF upload and processing.
"""

import streamlit as st
import logging
from pathlib import Path
from config.settings import UPLOAD_FOLDER, MAX_FILE_SIZE, APP_NAME
from modules.pdf_processor import PDFProcessor
from modules.text_cleaner import TextCleaner
from modules.question_extractor import QuestionExtractor
from modules.topic_classifier import TopicClassifier
from database.queries.paper_queries import PaperQueries
from database.queries.question_queries import QuestionQueries

logger = logging.getLogger(__name__)


def show_upload_page():
    """Display upload page content."""
    
    # Initialize session state
    if 'upload_status' not in st.session_state:
        st.session_state.upload_status = None
    
    # Upload section
    st.subheader("Step 1: Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose an exam paper PDF",
        type=["pdf"],
        help="Select a PDF file containing exam questions"
    )
    
    if uploaded_file is not None:
        # File info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📄 **File**: {uploaded_file.name}")
            st.write(f"📊 **Size**: {file_size_mb:.2f} MB")
        
        with col2:
            subject = st.text_input("Subject Name", value="Computer Science")
            year = st.number_input("Year", min_value=2010, max_value=2030, value=2024)
        
        # Validate file size
        if file_size_mb > (MAX_FILE_SIZE / (1024 * 1024)):
            st.error(f"❌ File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f} MB")
            return
        
        # Process button
        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                try:
                    # Save file
                    file_path = Path(UPLOAD_FOLDER) / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ File saved: {file_path}")
                    
                    # Step 1: Extract text
                    progress_bar = st.progress(0)
                    st.info("Step 1/4: Extracting text from PDF...")
                    
                    pdf_processor = PDFProcessor()
                    raw_text = pdf_processor.extract_text_from_pdf(str(file_path))
                    progress_bar.progress(25)
                    
                    st.success("✅ Text extracted")
                    
                    if not raw_text.strip() or len(raw_text) < 50:
                        st.warning(
                            "⚠️ **Warning**: The PDF appears to be a scanned image or contains minimal text. "
                            "Please ensure you're uploading text-based PDFs (not image scans). "
                            "The system requires PDFs with selectable text content."
                        )
                        return
                    
                    # Step 2: Clean text
                    st.info("Step 2/4: Cleaning text...")
                    cleaner = TextCleaner()
                    cleaned_text = cleaner.full_clean(raw_text)
                    progress_bar.progress(50)
                    
                    st.success("✅ Text cleaned")
                    
                    # Step 3: Extract questions
                    st.info("Step 3/4: Extracting questions...")
                    extractor = QuestionExtractor()
                    questions = extractor.extract_questions(cleaned_text)
                    progress_bar.progress(75)
                    
                    st.success(f"✅ Found {len(questions)} questions")
                    
                    # Step 4: Classify topics and store
                    st.info("Step 4/4: Classifying topics and storing...")
                    
                    # Store paper
                    try:
                        PaperQueries.create_paper(
                            subject=subject,
                            exam_title=uploaded_file.name.replace('.pdf', ''),
                            year=year,
                            exam_type='Final',
                            file_path=str(file_path),
                            file_size=uploaded_file.size
                        )
                        
                        # Get paper ID (simplified - in real app use insert ID)
                        papers = PaperQueries.get_papers_by_subject(subject)
                        paper_id = papers[-1]['id'] if papers else None
                        
                        if paper_id:
                            # Store questions
                            for question_text in questions:
                                question_data = extractor.parse_question_full(question_text)
                                topic = TopicClassifier.classify_question(question_text)
                                topic_id = None
                                
                                if topic:
                                    topic_id = TopicClassifier.get_topic_id_by_name(topic)
                                    if not topic_id:
                                        topic_id = TopicClassifier.create_missing_topic(topic)
                                
                                QuestionQueries.create_question(
                                    paper_id=paper_id,
                                    question_text=question_data['text'],
                                    topic_id=topic_id,
                                    question_type=question_data['type'],
                                    marks=question_data['marks']
                                )
                        
                        # Mark as processed
                        PaperQueries.update_paper_status(paper_id, True, len(questions))
                        
                    except Exception as db_error:
                        st.error(f"Database error: {db_error}")
                        logger.error(f"Database error: {db_error}")
                    
                    progress_bar.progress(100)
                    
                    st.success("✅ Processing complete!")
                    
                    # Display summary
                    st.markdown("---")
                    st.subheader("📋 Processing Summary")
                    
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    
                    with summary_col1:
                        st.metric("Questions Found", len(questions))
                    
                    with summary_col2:
                        st.metric("Text Length", f"{len(cleaned_text)} chars")
                    
                    with summary_col3:
                        st.metric("Subject", subject)
                    
                    # Show sample questions
                    st.subheader("Sample Extracted Questions")
                    for i, q in enumerate(questions[:3], 1):
                        st.write(f"**Q{i}:** {q[:100]}...")
                    
                    if len(questions) > 3:
                        st.info(f"...and {len(questions) - 3} more questions")
                    
                    st.session_state.upload_status = "success"
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Processing error: {e}")
                    st.session_state.upload_status = "error"
    
    else:
        st.info("👈 Upload a PDF to get started")
