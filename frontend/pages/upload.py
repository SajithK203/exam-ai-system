"""
Upload Page - Handle PDF upload and processing.
Enhanced with:
  - Duplicate detection via MD5 file hash
  - OCR fallback for scanned PDFs (graceful degradation)
  - Real difficulty inference (not always 'Medium')
  - MCQ option storage into question_options table
  - Accurate paper ID via LAST_INSERT_ID
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

    if 'upload_status' not in st.session_state:
        st.session_state.upload_status = None

    st.subheader("Step 1: Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose an exam paper PDF",
        type=["pdf"],
        help="Select a PDF file containing exam questions. Text-based and scanned PDFs are both supported."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_size_mb = len(file_bytes) / (1024 * 1024)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📄 **File**: {uploaded_file.name}")
            st.write(f"📊 **Size**: {file_size_mb:.2f} MB")
        with col2:
            subject = st.text_input("Subject Name", value="Computer Science")
            year = st.number_input("Year", min_value=2010, max_value=2030, value=2024)

        if file_size_mb > (MAX_FILE_SIZE / (1024 * 1024)):
            st.error(f"❌ File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f} MB")
            return

        # --- Duplicate detection ---
        file_hash = PDFProcessor.compute_file_hash(file_bytes)
        duplicate = PaperQueries.check_duplicate_by_hash(file_hash)
        if duplicate:
            st.warning(
                f"⚠️ **Duplicate Detected**: This exact file was already uploaded as "
                f"**'{duplicate.get('exam_title', 'Unknown')}'** "
                f"({duplicate.get('subject', '')} {duplicate.get('year', '')}). "
                "Upload a different file or rename to re-process."
            )
            return

        if st.button("🚀 Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                try:
                    # Save file
                    file_path = Path(UPLOAD_FOLDER) / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)
                    st.success(f"✅ File saved: {file_path}")

                    progress_bar = st.progress(0)

                    # Step 1: Extract text (with OCR fallback)
                    st.info("Step 1/4: Extracting text from PDF...")
                    pdf_processor = PDFProcessor()
                    raw_text, used_ocr = pdf_processor.extract_text_from_pdf(str(file_path))
                    progress_bar.progress(25)

                    if used_ocr:
                        st.info("🔍 **OCR Mode**: Scanned PDF detected — text extracted via Tesseract OCR.")
                    st.success("✅ Text extracted")

                    if not raw_text.strip() or len(raw_text.replace(" ", "").replace("\n", "")) < 50:
                        st.warning(
                            "⚠️ **Warning**: The PDF appears to contain minimal text. "
                            "Ensure the file has readable content. "
                            "If it is a scanned image PDF, install Tesseract OCR for full support."
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

                    # Step 4: Classify, infer difficulty, store
                    st.info("Step 4/4: Classifying topics, inferring difficulty, and storing...")

                    try:
                        # Store paper — get ID directly
                        paper_id = PaperQueries.create_paper(
                            subject=subject,
                            exam_title=uploaded_file.name.replace('.pdf', ''),
                            year=year,
                            exam_type='Final',
                            file_path=str(file_path),
                            file_size=uploaded_file.size,
                            file_hash=file_hash,
                        )

                        if paper_id:
                            ai_classified_count = 0
                            mcq_count = 0

                            for question_text in questions:
                                question_data = extractor.parse_question_full(question_text)

                                # Classify topic (rule-based + AI fallback)
                                topic, confidence, ai_used = TopicClassifier.classify_question(
                                    question_text, use_ai_fallback=True
                                )
                                if ai_used:
                                    ai_classified_count += 1

                                topic_id = None
                                if topic:
                                    topic_id = TopicClassifier.get_topic_id_by_name(topic)
                                    if not topic_id:
                                        topic_id = TopicClassifier.create_missing_topic(topic)

                                # Infer difficulty instead of defaulting to 'Medium'
                                difficulty = TopicClassifier.infer_difficulty(
                                    question_text, marks=question_data.get('marks')
                                )

                                # Store question — get inserted ID for options
                                question_id = QuestionQueries.create_question(
                                    paper_id=paper_id,
                                    question_text=question_data['text'],
                                    topic_id=topic_id,
                                    question_type=question_data['type'],
                                    marks=question_data.get('marks', 0),
                                    difficulty=difficulty,
                                    ai_classified=ai_used,
                                    topic_confidence=confidence,
                                )

                                # Store MCQ options if present
                                if question_data['type'] == 'Multiple Choice' and question_data.get('options'):
                                    mcq_count += 1
                                    if question_id:
                                        QuestionQueries.save_question_options(
                                            question_id, question_data['options']
                                        )

                            PaperQueries.update_paper_status(paper_id, True, len(questions))

                    except Exception as db_error:
                        st.error(f"Database error: {db_error}")
                        logger.error(f"Database error: {db_error}")

                    progress_bar.progress(100)
                    st.success("✅ Processing complete!")

                    # Summary
                    st.markdown("---")
                    st.subheader("📋 Processing Summary")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Questions Found", len(questions))
                    with col2:
                        st.metric("MCQ Questions", mcq_count)
                    with col3:
                        st.metric("AI Classified", ai_classified_count)
                    with col4:
                        st.metric("Mode", "OCR" if used_ocr else "Text")

                    # Show sample questions
                    st.subheader("Sample Extracted Questions")
                    for i, q in enumerate(questions[:3], 1):
                        st.write(f"**Q{i}:** {q[:120]}...")

                    if len(questions) > 3:
                        st.info(f"...and {len(questions) - 3} more questions stored in the Question Bank.")

                    st.session_state.upload_status = "success"

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Processing error: {e}")
                    st.session_state.upload_status = "error"

    else:
        st.info("👈 Upload a PDF to get started")
        st.markdown("""
        **Supported formats:**
        - ✅ Text-based PDFs (fastest)
        - ✅ Scanned/image PDFs (via OCR — requires Tesseract installed)
        
        **Duplicate protection:** The same file cannot be uploaded twice.
        """)
