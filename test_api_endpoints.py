#!/usr/bin/env python3
"""
Test the actual API endpoints to verify sessions and access_logs are created
"""

import requests
import json
import mysql.connector
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3306
}

def get_initial_counts():
    """Get current count of sessions and access logs"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM sessions")
    sessions_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM access_logs")
    logs_count = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return sessions_count, logs_count

def check_latest_records():
    """Check the latest records created"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    print("\n" + "="*70)
    print("LATEST SESSIONS:")
    print("="*70)
    cursor.execute("""
        SELECT session_id, user_id, wan_ip, status, login_time
        FROM sessions
        ORDER BY login_time DESC
        LIMIT 3
    """)
    sessions = cursor.fetchall()
    for s in sessions:
        print(f"  Session: {s['session_id'][:36]}")
        print(f"    User ID: {s['user_id']}, WAN IP: {s['wan_ip']}, Status: {s['status']}")
        print(f"    Login Time: {s['login_time']}\n")
    
    print("="*70)
    print("LATEST ACCESS LOGS:")
    print("="*70)
    cursor.execute("""
        SELECT log_id, session_id, user_id, endpoint, status_code, created_at
        FROM access_logs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            print(f"  Log ID: {log['log_id']}")
            print(f"    Endpoint: {log['endpoint']}, Status: {log['status_code']}")
            print(f"    User ID: {log['user_id']}, Session ID: {log['session_id'][:20] if log['session_id'] else 'None'}")
            print(f"    Created: {log['created_at']}\n")
    else:
        print("  No logs found\n")
    
    cursor.close()
    conn.close()

def test_failed_login():
    """Test failed login attempt"""
    print("\n" + "-"*70)
    print("TEST 1: FAILED LOGIN (wrong password)")
    print("-"*70)
    
    initial_sessions, initial_logs = get_initial_counts()
    print(f"Before: Sessions={initial_sessions}, Logs={initial_logs}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            data={"username": "admin1", "password": "wrongpassword"}
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    import time
    time.sleep(0.5)
    
    final_sessions, final_logs = get_initial_counts()
    print(f"After: Sessions={final_sessions}, Logs={final_logs}")
    print(f"Change: +{final_sessions - initial_sessions} sessions, +{final_logs - initial_logs} logs")
    
    if final_logs > initial_logs:
        print("✓ Access log was created")
    else:
        print("✗ No access log created")

def test_successful_login():
    """Test successful login"""
    print("\n" + "-"*70)
    print("TEST 2: SUCCESSFUL LOGIN")
    print("-"*70)
    
    initial_sessions, initial_logs = get_initial_counts()
    print(f"Before: Sessions={initial_sessions}, Logs={initial_logs}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            data={"username": "admin1", "password": "admin123"}
        )
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data.get('session_id', 'N/A')[:36]}")
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    import time
    time.sleep(0.5)
    
    final_sessions, final_logs = get_initial_counts()
    print(f"After: Sessions={final_sessions}, Logs={final_logs}")
    print(f"Change: +{final_sessions - initial_sessions} sessions, +{final_logs - initial_logs} logs")
    
    if final_sessions > initial_sessions:
        print("✓ Session was created")
    else:
        print("✗ No session created")
    
    if final_logs > initial_logs:
        print("✓ Access log was created")
    else:
        print("✗ No access log created")

def test_registration():
    """Test registration"""
    print("\n" + "-"*70)
    print("TEST 3: REGISTRATION")
    print("-"*70)
    
    initial_logs = get_initial_counts()[1]
    print(f"Before: Logs={initial_logs}")
    
    import time
    username = f"testuser_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/register",
            json={
                "username": username,
                "password": "password123",
                "confirm_password": "password123",
                "user_display_name": "Test User"
            }
        )
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)
    
    final_logs = get_initial_counts()[1]
    print(f"After: Logs={final_logs}")
    print(f"Change: +{final_logs - initial_logs} logs")
    
    if final_logs > initial_logs:
        print("✓ Access log was created")
    else:
        print("✗ No access log created")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("API ENDPOINT TESTING")
    print("="*70)
    print("\nNote: Make sure the API is running at http://localhost:8000")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"\n✓ API is running: {response.json()}")
    except:
        print(f"\n✗ API is NOT running at {API_BASE_URL}")
        print("  Start the API with: uvicorn main:app --reload")
        sys.exit(1)
    
    # Run tests
    test_failed_login()
    test_successful_login()
    test_registration()
    
    # Show results
    check_latest_records()
