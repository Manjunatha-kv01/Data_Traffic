#!/usr/bin/env python3
"""
Comprehensive test script to verify:
1. Session storage on login
2. Access logs storage for all endpoints
3. All data flows correctly to MySQL
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3306
}

def verify_database():
    """Verify database structure and data"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("\n" + "="*70)
        print("DATABASE VERIFICATION REPORT")
        print("="*70)
        
        # 1. Check tables exist
        print("\n1. TABLE EXISTENCE CHECK:")
        print("-" * 70)
        cursor.execute("SHOW TABLES LIKE 'users'")
        print(f"   users table:        {'✓ EXISTS' if cursor.fetchone() else '✗ MISSING'}")
        cursor.execute("SHOW TABLES LIKE 'sessions'")
        print(f"   sessions table:     {'✓ EXISTS' if cursor.fetchone() else '✗ MISSING'}")
        cursor.execute("SHOW TABLES LIKE 'access_logs'")
        print(f"   access_logs table:  {'✓ EXISTS' if cursor.fetchone() else '✗ MISSING'}")
        
        # 2. Check users
        print("\n2. USERS IN DATABASE:")
        print("-" * 70)
        cursor.execute("SELECT id, username, user_display_name, status, create_date FROM users LIMIT 10")
        users = cursor.fetchall()
        if users:
            for user in users:
                print(f"   User ID {user['id']:3d}: {user['username']:15s} - {user['user_display_name']}")
        else:
            print("   No users found")
        
        # 3. Check sessions
        print("\n3. SESSIONS IN DATABASE:")
        print("-" * 70)
        cursor.execute("""
            SELECT s.session_id, s.user_id, u.username, s.wan_ip, s.status, s.login_time
            FROM sessions s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.login_time DESC LIMIT 10
        """)
        sessions = cursor.fetchall()
        if sessions:
            print(f"   {'Session ID':<38} {'User':<15} {'WAN IP':<15} {'Status':<12} {'Login Time':<20}")
            print("   " + "-" * 100)
            for session in sessions:
                user = session.get('username', 'N/A') or 'N/A'
                print(f"   {str(session['session_id']):<38} {user:<15} {session['wan_ip']:<15} {session['status']:<12} {str(session['login_time']):<20}")
        else:
            print("   No sessions found")
        
        # 4. Check access_logs
        print("\n4. ACCESS LOGS IN DATABASE:")
        print("-" * 70)
        cursor.execute("""
            SELECT log_id, session_id, user_id, endpoint, method, status_code, wan_ip, created_at
            FROM access_logs
            ORDER BY created_at DESC LIMIT 20
        """)
        logs = cursor.fetchall()
        if logs:
            print(f"   {'ID':<5} {'Endpoint':<20} {'Method':<8} {'Status':<8} {'WAN IP':<15} {'Time':<20}")
            print("   " + "-" * 80)
            for log in logs:
                print(f"   {log['log_id']:<5} {log['endpoint']:<20} {log['method']:<8} {log['status_code']:<8} {log['wan_ip']:<15} {str(log['created_at']):<20}")
        else:
            print("   No access logs found")
        
        # 5. Access logs by endpoint
        print("\n5. ACCESS LOGS BY ENDPOINT:")
        print("-" * 70)
        cursor.execute("""
            SELECT endpoint, method, COUNT(*) as count, 
                   GROUP_CONCAT(DISTINCT status_code) as status_codes
            FROM access_logs
            GROUP BY endpoint, method
            ORDER BY endpoint
        """)
        endpoint_logs = cursor.fetchall()
        if endpoint_logs:
            for log in endpoint_logs:
                print(f"   {log['endpoint']:<25} {log['method']:<8} Count: {log['count']:<5} Status Codes: {log['status_codes']}")
        else:
            print("   No endpoint logs found")
        
        # 6. Access logs by status code
        print("\n6. ACCESS LOGS BY STATUS CODE:")
        print("-" * 70)
        cursor.execute("""
            SELECT status_code, COUNT(*) as count, endpoint
            FROM access_logs
            GROUP BY status_code
            ORDER BY status_code
        """)
        status_logs = cursor.fetchall()
        if status_logs:
            status_names = {
                200: "OK",
                201: "Created",
                400: "Bad Request",
                401: "Unauthorized",
                500: "Server Error"
            }
            for log in status_logs:
                status_name = status_names.get(log['status_code'], 'Unknown')
                print(f"   {log['status_code']:>3} {status_name:<20} - {log['count']:>5} occurrences")
        else:
            print("   No status logs found")
        
        # 7. Check data linkage
        print("\n7. DATA LINKAGE VERIFICATION:")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                al.endpoint,
                COUNT(*) as log_count,
                COUNT(DISTINCT al.session_id) as sessions_with_logs,
                COUNT(DISTINCT al.user_id) as users_accessed
            FROM access_logs al
            WHERE al.session_id IS NOT NULL
            GROUP BY al.endpoint
        """)
        linkage = cursor.fetchall()
        if linkage:
            print(f"   {'Endpoint':<25} {'Logs':<6} {'Sessions':<12} {'Users':<8}")
            print("   " + "-" * 55)
            for link in linkage:
                print(f"   {link['endpoint']:<25} {link['log_count']:<6} {link['sessions_with_logs']:<12} {link['users_accessed']:<8}")
        else:
            print("   No linked data found (endpoints without sessions)")
        
        # 8. Failed login attempts
        print("\n8. FAILED LOGIN ATTEMPTS (Status 401):")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                wan_ip,
                COUNT(*) as attempts,
                MAX(created_at) as last_attempt,
                GROUP_CONCAT(DISTINCT COALESCE(user_id, 'UNKNOWN')) as user_ids
            FROM access_logs
            WHERE endpoint = '/login' AND status_code = 401
            GROUP BY wan_ip
            ORDER BY attempts DESC
        """)
        failed_logins = cursor.fetchall()
        if failed_logins:
            print(f"   {'WAN IP':<15} {'Attempts':<10} {'Last Attempt':<20} {'User IDs'}")
            print("   " + "-" * 70)
            for login in failed_logins:
                print(f"   {login['wan_ip']:<15} {login['attempts']:<10} {str(login['last_attempt']):<20} {login['user_ids']}")
        else:
            print("   No failed login attempts found")
        
        # 9. Registration attempts
        print("\n9. REGISTRATION ATTEMPTS:")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                status_code,
                COUNT(*) as count
            FROM access_logs
            WHERE endpoint = '/register'
            GROUP BY status_code
            ORDER BY status_code
        """)
        registrations = cursor.fetchall()
        if registrations:
            status_names = {201: "Success", 400: "Validation Error", 500: "Server Error"}
            total = 0
            for reg in registrations:
                status_name = status_names.get(reg['status_code'], f"Status {reg['status_code']}")
                print(f"   {status_name:<20} - {reg['count']:>5} attempts")
                total += reg['count']
            print(f"   {'Total registrations':<20} - {total:>5}")
        else:
            print("   No registration attempts found")
        
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    verify_database()
