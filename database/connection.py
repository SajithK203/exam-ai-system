"""
Database connection management for MySQL (Aiven Cloud).
Uses PyMySQL (pure Python) for maximum compatibility with Streamlit Cloud.
"""

import logging

logger = logging.getLogger(__name__)


def _get_db_config():
    """
    Read DB credentials from Streamlit secrets (Streamlit Cloud)
    or environment variables (.env file for local dev).
    Called fresh every time so secrets are always available.
    """
    import os

    host = port = user = password = name = None

    # --- Try Streamlit secrets (priority 1) ---
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            host     = st.secrets.get("DB_HOST")
            port     = st.secrets.get("DB_PORT")
            user     = st.secrets.get("DB_USER")
            password = st.secrets.get("DB_PASSWORD")
            name     = st.secrets.get("DB_NAME")
    except Exception as e:
        logger.debug(f"Streamlit secrets not available: {e}")

    # --- Fall back to environment variables (priority 2) ---
    host     = (host     or os.getenv("DB_HOST",     "localhost")).strip()
    user     = (user     or os.getenv("DB_USER",     "root")).strip()
    password = str(password or os.getenv("DB_PASSWORD", "")).strip()
    name     = (name     or os.getenv("DB_NAME",     "exam_analysis_system")).strip()
    port     = int(str(port or os.getenv("DB_PORT",  "3306")).strip())

    logger.info(f"DB → host={host}  port={port}  db={name}  user={user}")

    return {
        "host":     host,
        "port":     port,
        "user":     user,
        "password": password,
        "database": name,
    }


def get_connection():
    """
    Open and return a fresh PyMySQL connection.
    SSL is configured to trust Aiven without a local CA certificate.
    """
    import pymysql
    import ssl as _ssl

    cfg = _get_db_config()

    # Build an SSL context that skips certificate verification
    # (Aiven enforces SSL but Streamlit Cloud doesn't have the Aiven CA cert)
    ssl_ctx = _ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = _ssl.CERT_NONE

    conn = pymysql.connect(
        host     = cfg["host"],
        port     = cfg["port"],
        user     = cfg["user"],
        password = cfg["password"],
        database = cfg["database"],
        charset  = "utf8mb4",
        autocommit = True,
        connect_timeout = 10,
        ssl      = ssl_ctx,
        cursorclass = pymysql.cursors.DictCursor,
    )
    return conn


class DatabaseConnection:
    """
    Thin wrapper kept for backward-compatibility with the rest of the codebase.
    All methods create a fresh connection — no pooling, no caching.
    """

    @classmethod
    def get_connection(cls):
        """Return a fresh database connection."""
        return get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and return results."""
        conn   = None
        cursor = None
        try:
            conn   = get_connection()
            cursor = conn.cursor()          # DictCursor already set at connect time
            cursor.execute(query, params or ())

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount

            conn.commit()
            return result
        except Exception as e:
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
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Database connection test PASSED")
        return True
    except Exception as e:
        logger.error(f"Database connection test FAILED: {e}")
        return False
