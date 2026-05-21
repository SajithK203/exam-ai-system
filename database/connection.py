"""
Database connection management for MySQL.
Handles connection pooling and query execution.
"""

import os
import streamlit as st
import mysql.connector
from mysql.connector import Error, pooling
import logging

logger = logging.getLogger(__name__)

# Database Configuration with Streamlit Secrets Support
DB_HOST = st.secrets.get("mysql-331df7c4-exam-ai.i.aivencloud.com") or os.getenv("mysql-331df7c4-exam-ai.i.aivencloud.com")
DB_PORT = st.secrets.get("DB_PORT") or os.getenv("DB_PORT", "17660")
DB_USER = st.secrets.get("DB_USER") or os.getenv("DB_USER", "avnadmin")
DB_PASSWORD = st.secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD", "AVNS_m2XAVFJOB3MV4EW0vBb")
DB_NAME = st.secrets.get("DB_NAME") or os.getenv("DB_NAME", "defaultdb")

# Create DB_CONFIG dictionary for backward compatibility
DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": int(DB_PORT),
    "autocommit": True,
    "use_unicode": True,
    "charset": "utf8mb4"
}


class DatabaseConnection:
    """Database connection handler with connection pooling."""
    
    _pool = None
    
    @classmethod
    def get_pool(cls):
        """Get or create connection pool."""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="exam_analysis_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **DB_CONFIG
                )
                logger.info("Connection pool created successfully")
            except Error as e:
                logger.error(f"Error creating connection pool: {e}")
                raise
        return cls._pool
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool."""
        try:
            pool = cls.get_pool()
            conn = pool.get_connection()
            logger.debug("Connection obtained from pool")
            return conn
        except Error as e:
            logger.error(f"Error getting connection: {e}")
            raise
    
    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """Execute query and return results."""
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
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
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @classmethod
    def close_pool(cls):
        """Close connection pool."""
        if cls._pool:
            try:
                cls._pool._cnx_queue.queue.clear()
                logger.info("Connection pool closed")
            except Exception as e:
                logger.error(f"Error closing pool: {e}")


def test_connection():
    """Test database connection."""
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Database connection test successful")
        return True
    except Error as e:
        logger.error(f"Database connection test failed: {e}")
        return False
