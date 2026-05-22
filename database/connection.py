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

# Import lazy config function - secrets are read at connection time, not import time
from config.settings import get_db_config


class DatabaseConnection:
    """Database connection handler with connection pooling."""
    
    _pool = None
    
    @classmethod
    def get_pool(cls):
        """Get or create connection pool."""
        if cls._pool is None:
            try:
                # Call get_db_config() here (not at import time) so that
                # Streamlit secrets are fully loaded before we read them.
                db_config = get_db_config()
                logger.info(f"Creating pool → host={db_config['host']} port={db_config['port']} db={db_config['database']}")
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="exam_analysis_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **db_config
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
    """Test database connection with detailed debug info."""
    try:
        # Read config lazily so secrets are available
        db_config = get_db_config()
        logger.info(f"Attempting connection to: {db_config['host']}:{db_config['port']}")
        logger.info(f"Database: {db_config['database']}, User: {db_config['user']}")
        
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("✅ Database connection test successful")
        return True
    except Error as e:
        logger.error(f"❌ MySQL Error: {e}")
        logger.error(f"Error Code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False
