"""
File Handler Utility - Handle file uploads and storage.
"""

import os
import logging
from pathlib import Path
from config.settings import UPLOAD_FOLDER, MAX_FILE_SIZE

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file operations."""
    
    @staticmethod
    def save_uploaded_file(uploaded_file, destination=None):
        """
        Save uploaded file to destination folder.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            destination: Custom destination path (optional)
            
        Returns:
            Path to saved file
        """
        try:
            if uploaded_file.size > MAX_FILE_SIZE:
                raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE} bytes")
            
            destination = destination or UPLOAD_FOLDER
            os.makedirs(destination, exist_ok=True)
            
            file_path = Path(destination) / uploaded_file.name
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            logger.info(f"File saved: {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    @staticmethod
    def delete_file(file_path):
        """Delete a file."""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in bytes."""
        try:
            file_path = Path(file_path)
            return file_path.stat().st_size
        except Exception as e:
            logger.error(f"Error getting file size: {e}")
            return 0
    
    @staticmethod
    def list_uploaded_files(folder=None):
        """List all uploaded files."""
        try:
            folder = folder or UPLOAD_FOLDER
            folder = Path(folder)
            
            if not folder.exists():
                return []
            
            files = [f.name for f in folder.iterdir() if f.is_file()]
            return sorted(files)
        
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    @staticmethod
    def cleanup_old_files(days=7, folder=None):
        """Delete files older than N days."""
        try:
            import time
            
            folder = folder or UPLOAD_FOLDER
            folder = Path(folder)
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            deleted = 0
            for file in folder.iterdir():
                if file.is_file() and file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    deleted += 1
            
            logger.info(f"Cleaned up {deleted} old files")
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            return 0
