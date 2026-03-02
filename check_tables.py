#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3306
}

def check_tables():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check access_logs
        cursor.execute("SHOW TABLES LIKE 'access_logs'")
        access_logs_exists = cursor.fetchone() is not None
        
        # Check sessions
        cursor.execute("SHOW TABLES LIKE 'sessions'")
        sessions_exists = cursor.fetchone() is not None
        
        print("=" * 60)
        print("DATABASE TABLE CHECK")
        print("=" * 60)
        print(f"access_logs table: {'✓ EXISTS' if access_logs_exists else '✗ MISSING'}")
        print(f"sessions table:    {'✓ EXISTS' if sessions_exists else '✗ MISSING'}")
        print("=" * 60)
        
        if access_logs_exists:
            cursor.execute("DESCRIBE access_logs")
            columns = cursor.fetchall()
            print("\naccess_logs columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        
        if sessions_exists:
            cursor.execute("DESCRIBE sessions")
            columns = cursor.fetchall()
            print("\nsessions columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        
        return access_logs_exists, sessions_exists
        
    except Error as e:
        print(f"Database Error: {e}")
        return False, False

if __name__ == "__main__":
    check_tables()
