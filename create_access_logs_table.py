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

CREATE_ACCESS_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS `access_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `endpoint` varchar(255) NOT NULL COMMENT 'API endpoint called',
  `method` varchar(10) NOT NULL COMMENT 'HTTP method (GET, POST, etc)',
  `status_code` int(11) NOT NULL COMMENT 'HTTP status code',
  `wan_ip` varchar(50) NOT NULL COMMENT 'Client IP address',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_endpoint` (`endpoint`),
  KEY `idx_status_code` (`status_code`),
  KEY `idx_wan_ip` (`wan_ip`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_endpoint_status` (`endpoint`, `status_code`),
  KEY `idx_wan_ip_created` (`wan_ip`, `created_at`),
  CONSTRAINT `fk_access_logs_session_id` FOREIGN KEY (`session_id`) 
    REFERENCES `sessions`(`session_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_access_logs_user_id` FOREIGN KEY (`user_id`) 
    REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
"""

def create_table():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Creating access_logs table...")
        cursor.execute(CREATE_ACCESS_LOGS_TABLE)
        conn.commit()
        
        cursor.execute("DESCRIBE access_logs")
        columns = cursor.fetchall()
        
        print("\n✓ access_logs table created successfully!")
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
