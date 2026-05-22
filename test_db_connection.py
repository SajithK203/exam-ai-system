#!/usr/bin/env python
"""
Database diagnostic script to test MySQL connection
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import DB_CONFIG
import mysql.connector
from mysql.connector import Error

print("=" * 60)
print("DATABASE DIAGNOSTIC")
print("=" * 60)

print("\n1. Checking .env configuration:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   User: {DB_CONFIG['user']}")
print(f"   Password: {'*' * len(DB_CONFIG['password']) if DB_CONFIG['password'] else '(empty)'}")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   Port: {DB_CONFIG['port']}")

print("\n2. Testing raw MySQL connection (no database selection):")
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("   [OK] Connected to MySQL server successfully!")
    
    # Check if database exists
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE %s", (DB_CONFIG['database'],))
    result = cursor.fetchone()
    
    if result:
        print(f"   [OK] Database '{DB_CONFIG['database']}' exists")
        
        # Check tables
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", (DB_CONFIG['database'],))
        table_count = cursor.fetchone()[0]
        print(f"   [OK] Database has {table_count} tables")
        
        if table_count == 0:
            print("   [WARN] Database exists but has NO tables - schema not loaded!")
            cursor.execute("SHOW DATABASES")
            all_dbs = [row[0] for row in cursor.fetchall()]
            print(f"   [INFO] Available databases on server: {all_dbs}")
    else:
        print(f"   [ERROR] Database '{DB_CONFIG['database']}' DOES NOT EXIST")
        cursor.execute("SHOW DATABASES")
        all_dbs = [row[0] for row in cursor.fetchall()]
        print(f"   [INFO] Available databases on server: {all_dbs}")
        print("   [WARN] Run: Get-Content database/schema.sql | mysql -u root -p1234 exam_analysis_system")
    
    cursor.close()
    conn.close()
    
except Error as e:
    print(f"   [ERROR] Connection failed: {e}")
    print(f"   Error code: {e.errno}")
    
    if e.errno == 1045:
        print("   [ERROR] Access denied - wrong password or user doesn't exist")
    elif e.errno == 2003:
        print("   [ERROR] Can't connect to MySQL server - is it running?")

print("\n" + "=" * 60)
