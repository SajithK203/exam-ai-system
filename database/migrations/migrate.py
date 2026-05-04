"""
Database Migration Script - Initialize all tables and seed data.
"""

import logging
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


def run_migrations():
    """
    Run all database migrations.
    This initializes the database schema.
    """
    try:
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute each statement
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                DatabaseConnection.execute_query(statement)
                logger.info(f"Executed migration: {statement[:50]}...")
        
        logger.info("✅ All migrations completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
