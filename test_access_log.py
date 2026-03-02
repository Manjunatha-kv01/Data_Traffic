#!/usr/bin/env python3
"""
Test if create_access_log function works correctly
"""

import sys
sys.path.insert(0, '/Users/manjunathkv/Data_Traffic')

from database import create_access_log
import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3306
}

print("\n" + "="*70)
print("TESTING ACCESS_LOG CREATION FUNCTION")
print("="*70)

# Test 1: Log a failed login attempt
print("\nTest 1: Failed Login Attempt (401)")
result = create_access_log(
    session_id=None,
    user_id=None,
    endpoint="/login",
    method="POST",
    status_code=401,
    wan_ip="127.0.0.1"
)
print(f"Result: {result}")

# Test 2: Log a successful login
print("\nTest 2: Successful Login (200)")
result = create_access_log(
    session_id="test-session-123",
    user_id=1,
    endpoint="/login",
    method="POST",
    status_code=200,
    wan_ip="127.0.0.1"
)
print(f"Result: {result}")

# Test 3: Log a registration failure
print("\nTest 3: Registration Validation Failure (400)")
result = create_access_log(
    session_id=None,
    user_id=None,
    endpoint="/register",
    method="POST",
    status_code=400,
    wan_ip="192.168.1.1"
)
print(f"Result: {result}")

# Test 4: Log an API access
print("\nTest 4: API Access (200)")
result = create_access_log(
    session_id="test-session-456",
    user_id=2,
    endpoint="/traffic/summary",
    method="POST",
    status_code=200,
    wan_ip="127.0.0.1"
)
print(f"Result: {result}")

# Check if logs were created
print("\n" + "-"*70)
print("Checking if logs were created...")
print("-"*70)

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM access_logs")
    result = cursor.fetchone()
    log_count = result['count']
    
    print(f"\nTotal access logs in database: {log_count}")
    
    if log_count > 0:
        print("\nLatest access logs:")
        cursor.execute("""
            SELECT log_id, session_id, user_id, endpoint, status_code, wan_ip, created_at
            FROM access_logs
            ORDER BY log_id DESC
            LIMIT 10
        """)
        logs = cursor.fetchall()
        for log in logs:
            print(f"  {log['endpoint']:<20} {log['method'] if 'method' in log else 'N/A':<8} Status: {log['status_code']:<5} User: {str(log['user_id']):<5} Session: {str(log['session_id']):<20}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error checking logs: {e}")

print("\n" + "="*70 + "\n")
