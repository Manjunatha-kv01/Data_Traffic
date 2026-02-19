import mysql.connector
from mysql.connector import Error
from typing import Optional, Tuple, List
import uuid

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3306
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
        return None


def get_user_by_username(username: str) -> Optional[dict]:
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB error in get_user_by_username: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def create_user(username: str, password: str, user_display_name: str = None) -> Tuple[bool, str]:
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO users (username, password, user_display_name, status)
            VALUES (%s, %s, %s, 1)
        """
        cursor.execute(query, (username, password, user_display_name or username))
        conn.commit()
        return True, "User created successfully"
    except Error as e:
        print("DB error in create_user:", e)
        return False, "Database error"
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def user_exists_in_db(username: str) -> bool:
    return get_user_by_username(username) is not None


def get_traffic_by_time_range(wan_ip: str, from_time: str, to_time: str) -> Tuple[List[dict], int]:
    conn = get_db_connection()
    if not conn:
        return None, 0

    try:
        cursor = conn.cursor(dictionary=True)

        data_query = """
        SELECT 
            time_hour,
            wan_ip,
            in_avg,
            out_avg,
            in_max,
            out_max
        FROM traffic_hourly_copy
        WHERE wan_ip = %s
          AND time_hour BETWEEN %s AND %s
        ORDER BY time_hour ASC
        """

        count_query = """
        SELECT COUNT(*) AS total_rows
        FROM traffic_hourly_copy
        WHERE wan_ip = %s
          AND time_hour BETWEEN %s AND %s
        """

        cursor.execute(data_query, (wan_ip, from_time, to_time))
        rows = cursor.fetchall()

        cursor.execute(count_query, (wan_ip, from_time, to_time))
        row = cursor.fetchone()
        count = row["total_rows"] if row else 0

        return rows, count

    except Error as e:
        print("DB error in get_traffic_by_time_range:", e)
        return None, 0
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def get_traffic_dashboard_by_location_wanip(location: str, wan_ip: str, from_time: str, to_time: str):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            b.node AS location,
            t.wan_ip,
            b.bandwidth,
            COUNT(*) AS data_points,
            ROUND(AVG(t.in_traffic), 2) AS avg_in,
            ROUND(AVG(t.out_traffic), 2) AS avg_out,
            MAX(t.in_traffic) AS peak_in,
            MAX(t.out_traffic) AS peak_out,
            MIN(t.reading_time) AS first_reading,
            MAX(t.reading_time) AS last_reading
        FROM traffic_logs t
        JOIN bmap_link_master b ON b.wanip = t.wan_ip
        WHERE b.node = %s
          AND t.wan_ip = %s
          AND t.reading_time BETWEEN %s AND %s
        GROUP BY b.node, t.wan_ip, b.bandwidth
        """

        cursor.execute(query, (location, wan_ip, from_time, to_time))
        return cursor.fetchone()

    except Error as e:
        print(f"DB error in get_traffic_dashboard_by_location_wanip: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def get_traffic_dashboard_by_location(location: str, from_time: str, to_time: str):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            b.node AS location,
            t.wan_ip,
            b.interface,
            b.description,
            b.bandwidth,
            COUNT(*) AS data_points,
            ROUND(AVG(t.in_avg), 2) AS avg_in,
            ROUND(AVG(t.out_avg), 2) AS avg_out,
            MAX(t.in_max) AS peak_in,
            MAX(t.out_max) AS peak_out,
            MIN(t.time_hour) AS first_reading,
            MAX(t.time_hour) AS last_reading
        FROM traffic_hourly_copy t
        JOIN bmap_link_master b ON b.wanip = t.wan_ip
        WHERE b.node = %s
          AND t.time_hour BETWEEN %s AND %s
        GROUP BY b.node, t.wan_ip, b.interface, b.description, b.bandwidth
        ORDER BY t.wan_ip
        """

        cursor.execute(query, (location, from_time, to_time))
        return cursor.fetchall()

    except Error as e:
        print(f"DB error in get_traffic_dashboard_by_location: {e}")
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def get_user_activity_by_wan_ip(wan_ip: str, from_time: str, to_time: str):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            u.id AS user_id,
            u.username,
            u.user_display_name,
            ur.resource_name,
            us.resource_value,
            blm.wanip AS wan_ip,
            s.login_time,
            s.logout_time
        FROM users_scope us
        JOIN users u 
            ON u.id = us.user_id
        JOIN users_resource ur 
            ON ur.resource_id = us.resource_id
        LEFT JOIN bmap_link_master blm 
            ON blm.wanip = us.resource_value
        LEFT JOIN sessions s 
            ON s.user_id = u.id AND s.wan_ip = blm.wanip
        WHERE ur.resource_name = 'WANIP'
          AND blm.wanip = %s
          AND s.login_time BETWEEN %s AND %s
        ORDER BY s.login_time DESC
        """

        cursor.execute(query, (wan_ip, from_time, to_time))
        return cursor.fetchall()

    except Exception as e:
        print("DB error in get_user_activity_by_wan_ip:", e)
        return []
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def create_session(user_id: int, username: str, wan_ip: str):
    conn = get_db_connection()
    if not conn:
        print("DB connection failed in create_session")
        return None

    try:
        session_id = str(uuid.uuid4())
        cursor = conn.cursor()
        query = """
        INSERT INTO sessions (session_id, user_id, wan_ip, status)
        VALUES (%s, %s, %s, 'ACTIVE')
        """
        cursor.execute(query, (session_id, user_id, wan_ip))
        conn.commit()
        return session_id
    except Error as e:
        print("DB error in create_session:", e)
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def close_session(session_id: str):
    conn = get_db_connection()
    if not conn:
        print("DB connection failed in close_session")
        return False

    try:
        cursor = conn.cursor()
        query = """
        UPDATE sessions
        SET logout_time = NOW(), status = 'LOGGED_OUT'
        WHERE session_id = %s
        """
        cursor.execute(query, (session_id,))
        conn.commit()
        return True
    except Error as e:
        print("DB error in close_session:", e)
        return False
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def create_access_log(
    session_id: Optional[str],
    user_id: Optional[int],
    endpoint: str,
    method: str,
    status_code: int,
    wan_ip: str
):
    conn = get_db_connection()
    if not conn:
        print("DB connection failed in create_access_log")
        return False

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO access_logs 
        (session_id, user_id, endpoint, method, status_code, wan_ip)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (session_id, user_id, endpoint, method, status_code, wan_ip))
        conn.commit()
        return True
    except Error as e:
        print("DB error in create_access_log:", e)
        return False
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
