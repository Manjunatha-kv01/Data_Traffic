import mysql.connector
from mysql.connector import Error
from typing import Optional, Tuple, List

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "customer_portal",
    "port": 3307
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
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
        user = cursor.fetchone()
        return user
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
        count = cursor.fetchone()["total_rows"]

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


def get_traffic_summary_by_location(from_time: str, to_time: str, location: str = None) -> List[dict]:
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        conditions = ["t.time_hour BETWEEN %s AND %s"]
        params = [from_time, to_time]

        if location:
            conditions.append("b.node = %s")
            params.append(location)

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            b.node AS location,
            b.wanip AS wan_ip,
            b.bandwidth,
            COUNT(*) AS data_points,
            ROUND(AVG(t.in_avg), 2) AS avg_in,
            ROUND(AVG(t.out_avg), 2) AS avg_out,
            ROUND(MAX(t.in_max), 2) AS peak_in,
            ROUND(MAX(t.out_max), 2) AS peak_out,
            MIN(t.time_hour) AS first_reading,
            MAX(t.time_hour) AS last_reading
        FROM bmap_link_master b
        INNER JOIN traffic_hourly_copy t ON t.wan_ip = b.wanip
        WHERE {where_clause}
        GROUP BY b.node, b.wanip, b.bandwidth
        ORDER BY b.node ASC
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print("DB error in get_traffic_summary_by_location:", e)
        return []
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
            a.logout_time
        FROM users_scope us
        JOIN users u 
            ON u.id = us.user_id
        JOIN users_resource ur 
            ON ur.resource_id = us.resource_id
        LEFT JOIN bmap_link_master blm 
            ON blm.wanip = us.resource_value
        LEFT JOIN session s 
            ON s.user_id = u.id AND s.wan_ip = blm.wanip
        LEFT JOIN access a 
            ON a.user_id = u.id AND a.wan_ip = blm.wanip
        WHERE ur.resource_name = 'WANIP'
          AND blm.wanip = %s
          AND s.login_time BETWEEN %s AND %s
        ORDER BY s.login_time DESC
        """

        cursor.execute(query, (wan_ip, from_time, to_time))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print("DB error in get_user_activity_by_wan_ip:", e)
        return []
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
