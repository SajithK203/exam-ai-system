"""
Application Entry Point - Main runner script.
Run this to start the application.
"""

import streamlit as st
import sys
import logging
from config.settings import APP_NAME, APP_VERSION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Import and run frontend
        from frontend.app import show_upload_page
        
        # This will be replaced by Streamlit's page routing
        logger.info("Application started successfully")
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Note: This file is primarily for reference.
    # Start the app using: streamlit run frontend/app.py
    print(f"🚀 {APP_NAME} v{APP_VERSION}")
    print("To start the application, run:")
    print("  streamlit run frontend/app.py")
