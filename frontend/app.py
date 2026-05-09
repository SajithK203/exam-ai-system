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
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dashboard Custom CSS
st.markdown("""
<style>
    /* Main Backgrounds */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Navigation Buttons */
    div[data-testid="stSidebarNav"] {display: none;} /* Hide default Streamlit sidebar nav just in case */
    
    .nav-btn {
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s ease;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .nav-btn:hover {
        background: #334155;
        color: #f8fafc;
    }
    
    /* We handle active state via Streamlit native buttons mapped via session state now, 
       but we style the generic streamlit buttons in the sidebar here */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border: none;
        background-color: transparent;
        color: #94a3b8;
        text-align: left;
        justify-content: flex-start;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #334155;
        color: #f8fafc;
        border-color: transparent;
    }
    
    [data-testid="stSidebar"] .stButton > button:focus:not(:active) {
        border-color: transparent;
        color: #f8fafc;
        box-shadow: none;
    }
    
    /* Metrics Cards */
    [data-testid="stMetricValue"] {
        color: #7c3aed;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.875rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-card-container {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #334155;
        border-top: 3px solid #7c3aed;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Info Cards (How it works / Features) */
    .info-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.2s;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        border-color: #7c3aed;
    }
    
    .info-card h4 {
        color: #06b6d4 !important;
        margin-top: 0;
    }
    
    /* Hero Section */
    .hero-banner {
        background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%);
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .hero-banner h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-banner p {
        color: #e2e8f0;
        font-size: 1.1rem;
        margin-top: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State for Navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def nav_to(page_name):
    st.session_state.current_page = page_name

# Sidebar Navigation
with st.sidebar:
    st.markdown(f"## 🎓 {APP_NAME}")
    st.caption(f"v{APP_VERSION} | Educational Intelligence")
    st.divider()
    
    st.markdown("### 📌 MAIN MENU")
    
    # Custom Button Navigation
    if st.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == "Dashboard" else "secondary"):
        nav_to("Dashboard")
        
    if st.button("📤 Upload Paper", use_container_width=True, type="primary" if st.session_state.current_page == "Upload" else "secondary"):
        nav_to("Upload")
        
    if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state.current_page == "Analytics" else "secondary"):
        nav_to("Analytics")
        
    if st.button("❓ Question Bank", use_container_width=True, type="primary" if st.session_state.current_page == "Questions" else "secondary"):
        nav_to("Questions")
        
    if st.button("🤖 Study Insights", use_container_width=True, type="primary" if st.session_state.current_page == "Insights" else "secondary"):
        nav_to("Insights")
        
    if st.button("📝 Mock Exam", use_container_width=True, type="primary" if st.session_state.current_page == "Mock Exam" else "secondary"):
        nav_to("Mock Exam")
    
    st.divider()
    
    # System Status Badge
    st.markdown("### 📡 SYSTEM STATUS")
    if test_connection():
        st.markdown("""
        <div style="padding: 0.5rem 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 0.5rem; color: #10b981; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></div>
            Database Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 0.5rem 1rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 0.5rem; color: #ef4444; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #ef4444;"></div>
            Database Error
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    st.caption("Powered by Streamlit + Groq AI")

# Main content area routing
page = st.session_state.current_page

if page == "Dashboard":
    # Hero Section
    st.markdown("""
    <div class="hero-banner">
        <h1>Educational Intelligence Platform</h1>
        <p>Transform past exam papers into actionable study insights, dynamic question banks, and targeted mock exams.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Metrics Row
    st.markdown("### 📊 System Metrics")
    try:
        from database.queries.paper_queries import PaperQueries
        from database.queries.analytics_queries import AnalyticsQueries
        
        paper_count = PaperQueries.get_paper_count()
        # Simplified query to get total topics/questions for dashboard
        subjects = PaperQueries.get_unique_subjects()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card-container">', unsafe_allow_html=True)
            st.metric("Total Papers", paper_count)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-container" style="border-top-color: #06b6d4;">', unsafe_allow_html=True)
            st.metric("Active Subjects", len(subjects) if subjects else 0)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-container" style="border-top-color: #10b981;">', unsafe_allow_html=True)
            st.metric("Database Status", "Online")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card-container" style="border-top-color: #f59e0b;">', unsafe_allow_html=True)
            st.metric("AI Engine", "Ready")
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.warning(f"Could not load live stats: {e}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("### 🚀 How It Works")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>1. Upload 📤</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Upload past exam papers in PDF format. Our AI extracts text and structure automatically.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>2. Analyze 📊</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">The system parses questions, classifies topics, and maps difficulty distributions.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>3. Insights 🤖</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Generate intelligent study plans focusing on weak areas and high-frequency topics.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="info-card">
            <h4>4. Practice 📝</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Generate customized mock exams perfectly matching historical patterns to test readiness.</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Upload":
    from frontend.pages.upload import show_upload_page
    show_upload_page()

elif page == "Analytics":
    st.title("📊 Analysis Dashboard")
    st.markdown("Visualize exam patterns and topic frequencies")
    from frontend.pages.analysis import show_analysis_page
    show_analysis_page()

elif page == "Questions":
    st.title("❓ Question Bank")
    st.markdown("Browse and search extracted exam questions")
    from frontend.pages.questions import show_questions_page
    show_questions_page()

elif page == "Insights":
    st.title("🤖 Study Insights")
    st.markdown("Get personalized academic recommendations from AI")
    from frontend.pages.insights import show_insights_page
    show_insights_page()

elif page == "Mock Exam":
    st.title("📝 Mock Exam Generator")
    st.markdown("Create practice exams based on historical patterns")
    from frontend.pages.mock_exam import show_mock_exam_page
    show_mock_exam_page()

# Footer
st.divider()
st.caption("© 2024 AI Exam Analysis System | Confidential Educational Intelligence Platform")

