-- ===================================================================
-- Table: access_logs
-- Purpose: Log all API access attempts, including successful and failed 
--          login/registration attempts with WAN IP tracking
-- ===================================================================

CREATE TABLE IF NOT EXISTS `access_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `endpoint` varchar(255) NOT NULL COMMENT 'API endpoint called (e.g., /login, /register, /traffic/summary)',
  `method` varchar(10) NOT NULL COMMENT 'HTTP method (GET, POST, PUT, DELETE, etc)',
  `status_code` int(11) NOT NULL COMMENT 'HTTP response status code (200, 401, 400, 500, etc)',
  `wan_ip` varchar(50) NOT NULL COMMENT 'WAN IP address of the client',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when log was created',
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

-- ===================================================================
-- Index Strategy for access_logs:
-- - idx_session_id: Find all access logs for a session
-- - idx_user_id: Find all access logs by user
-- - idx_endpoint: Find all accesses to a specific endpoint
-- - idx_status_code: Find failed/successful access attempts
-- - idx_wan_ip: Find all accesses from a specific WAN IP (security)
-- - idx_created_at: Time-based queries for audit
-- - idx_endpoint_status: Join endpoint and status for audit reports
-- - idx_wan_ip_created: Find recent activities from specific IPs
-- ===================================================================
