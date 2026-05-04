"""
Main Streamlit Application Entry Point
Dashboard and navigation for the exam analysis system.
"""

import streamlit as st
import logging
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import STREAMLIT_CONFIG, APP_NAME, APP_VERSION
from database.connection import test_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Streamlit
st.set_page_config(**STREAMLIT_CONFIG)

# Sidebar styling
with st.sidebar:
    st.title(f"📚 {APP_NAME}")
    st.caption(f"v{APP_VERSION}")
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        options=[
            "🏠 Home",
            "📤 Upload Paper",
            "📊 Analysis Dashboard",
            "❓ Questions",
            "🤖 AI Insights",
            "📝 Mock Exam"
        ],
        key="navigation"
    )
    
    st.divider()
    
    # System Status
    st.subheader("System Status")
    if test_connection():
        st.success("✅ Database Connected")
    else:
        st.error("❌ Database Error")
    
    st.divider()
    st.caption("AI Exam Analysis System")

# Main content area
if page == "🏠 Home":
    st.title("Welcome to AI Exam Analysis System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What This System Does
        
        This intelligent system helps you ace your exams by:
        
        - 📄 **Analyzing Past Papers**: Upload exam PDFs and extract questions automatically
        - 📊 **Pattern Recognition**: Identify most frequently asked topics
        - 🤖 **Smart Recommendations**: Get AI-powered study guidance
        - ❓ **Question Bank**: Access all extracted questions organized by topic
        - 📝 **Mock Exams**: Generate practice papers based on exam patterns
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Upload Papers**: Start by uploading exam PDFs
        2. **Extract Questions**: System automatically parses questions
        3. **View Analysis**: See topic frequency and patterns
        4. **Get Insights**: AI generates personalized recommendations
        5. **Practice**: Generate and take mock exams
        
        ### 📈 Key Features
        
        ✅ Automatic question extraction  
        ✅ Topic classification  
        ✅ Frequency analysis  
        ✅ AI-powered recommendations  
        ✅ Mock exam generation  
        """)
    
    st.divider()
    
    # Feature highlights
    st.subheader("📌 Quick Stats")
    
    try:
        from database.queries.paper_queries import PaperQueries
        from database.queries.question_queries import QuestionQueries
        
        paper_count = PaperQueries.get_paper_count()
        
        # Note: This would need actual question count logic
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Papers Uploaded", paper_count)
        
        with col2:
            st.metric("❓ Questions Extracted", "Loading...")
        
        with col3:
            st.metric("📚 Topics Identified", "Loading...")
    
    except Exception as e:
        st.warning(f"Could not load stats: {e}")
    
    st.info("👉 Start by uploading an exam paper using the '📤 Upload Paper' option in the sidebar!")

elif page == "📤 Upload Paper":
    st.title("📤 Upload Exam Paper")
    st.markdown("Upload PDF exam papers for automatic analysis")
    from frontend.pages.upload import show_upload_page
    show_upload_page()

elif page == "📊 Analysis Dashboard":
    st.title("📊 Analysis Dashboard")
    st.markdown("Visualize exam patterns and topic frequencies")
    from frontend.pages.analysis import show_analysis_page
    show_analysis_page()

elif page == "❓ Questions":
    st.title("❓ Question Bank")
    st.markdown("Browse and search extracted exam questions")
    from frontend.pages.questions import show_questions_page
    show_questions_page()

elif page == "🤖 AI Insights":
    st.title("🤖 AI Insights & Recommendations")
    st.markdown("Get personalized study recommendations from AI")
    from frontend.pages.insights import show_insights_page
    show_insights_page()

elif page == "📝 Mock Exam":
    st.title("📝 Mock Exam Generator")
    st.markdown("Create practice exams based on exam patterns")
    from frontend.pages.mock_exam import show_mock_exam_page
    show_mock_exam_page()

# Footer
st.divider()
st.caption("© 2024 AI Exam Analysis System | Powered by Streamlit + Groq AI")
