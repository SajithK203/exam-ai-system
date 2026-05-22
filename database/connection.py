"""
Database connection management for MySQL (Aiven Cloud).
Uses direct connections (no pooling) to ensure secrets are
read fresh at runtime on Streamlit Cloud.
"""

import mysql.connector
from mysql.connector import Error
import logging

logger = logging.getLogger(__name__)


def _get_db_config():
    """
    Read DB configuration from Streamlit secrets or environment variables.
    Called fresh every time a connection is needed so that
    st.secrets is fully initialised before we read it.
    """
    import os
    import sys

    # Try Streamlit secrets first (Streamlit Cloud production)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            host     = st.secrets.get("DB_HOST")
            port     = st.secrets.get("DB_PORT")
            user     = st.secrets.get("DB_USER")
            password = st.secrets.get("DB_PASSWORD")
            name     = st.secrets.get("DB_NAME")

            if host and host.strip():
                logger.info(f"DB config loaded from Streamlit secrets → host={host}")
                return {
                    "host":                host.strip(),
                    "port":                int(str(port).strip()) if port else 3306,
                    "user":                user.strip() if user else "root",
                    "password":            str(password).strip() if password else "",
                    "database":            name.strip() if name else "defaultdb",
                    "autocommit":          True,
                    "use_unicode":         True,
                    "charset":             "utf8mb4",
                    "ssl_disabled":        False,
                    "ssl_verify_cert":     False,
                    "ssl_verify_identity": False,
                    "connection_timeout":  10,
                }
    except Exception as e:
        logger.warning(f"Could not read from Streamlit secrets: {e}")

    # Fall back to environment variables (local .env)
    host = os.getenv("DB_HOST", "localhost")
    logger.info(f"DB config loaded from environment → host={host}")
    return {
        "host":                os.getenv("DB_HOST", "localhost"),
        "port":                int(os.getenv("DB_PORT", "3306")),
        "user":                os.getenv("DB_USER", "root"),
        "password":            os.getenv("DB_PASSWORD", ""),
        "database":            os.getenv("DB_NAME", "exam_analysis_system"),
        "autocommit":          True,
        "use_unicode":         True,
        "charset":             "utf8mb4",
        "ssl_disabled":        False,
        "ssl_verify_cert":     False,
        "ssl_verify_identity": False,
        "connection_timeout":  10,
    }


def get_connection():
    """Open and return a fresh MySQL connection (no pooling)."""
    config = _get_db_config()
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        logger.error(f"Error connecting to MySQL at {config['host']}:{config['port']} — {e}")
        raise


class DatabaseConnection:
    """
    Thin wrapper around get_connection() kept for backward-compatibility
    with the rest of the code that calls DatabaseConnection.get_connection()
    or DatabaseConnection.execute_query().
    """

    @classmethod
    def get_connection(cls):
        """Get a fresh direct connection."""
        return get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and return results."""
        conn   = None
        cursor = None
        try:
            conn   = cls.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount

            conn.commit()
            return result
        except Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


def test_connection():
    """Test database connection — used by the sidebar status badge."""
    try:
        config = _get_db_config()
        logger.info(f"Testing connection → host={config['host']} port={config['port']} db={config['database']}")
        conn   = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Database connection test PASSED")
        return True
    except Error as e:
        logger.error(f"Database connection test FAILED: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {type(e).__name__}: {e}")
        return False
