# Data Traffic API

A RESTful API built with FastAPI for monitoring and managing network traffic data with JWT-based authentication.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Known Issues & Recommendations](#known-issues--recommendations)
- [License](#license)

---

## Overview

Data Traffic API is a backend service designed to:
- Manage user authentication and authorization
- Retrieve and analyze network traffic data based on WAN IP addresses
- Provide secure access to traffic metrics through JWT tokens

---

## Features

- **User Registration & Authentication**: Secure user signup and login with JWT tokens
- **Password Security**: Supports bcrypt hashing for password storage
- **Traffic Data Retrieval**: Query traffic statistics by WAN IP and time range
- **Dashboard Summary**: Get aggregated traffic data by location
- **User Activity History**: Track user access patterns by WAN IP
- **OAuth2 Compatible**: Uses OAuth2 password flow for authentication
- **Input Validation**: Pydantic-based request/response validation
- **RESTful Design**: Clean and intuitive API endpoints

---

## Technology Stack

| Component          | Technology                      |
|--------------------|---------------------------------|
| **Framework**      | FastAPI 0.128.0                 |
| **Database**       | MySQL / MariaDB                 |
| **ORM/Connector**  | mysql-connector-python          |
| **Authentication** | JWT (python-jose)               |
| **Password Hashing** | bcrypt (passlib)              |
| **Validation**     | Pydantic                        |
| **Server**         | Uvicorn                         |

---

## Project Structure

```
Data.traffic/
├── main.py           # FastAPI application and route definitions
├── auth.py           # Authentication utilities (JWT, password hashing)
├── database.py       # Database connection and queries
├── models.py         # Pydantic data models
├── Data.sql.sql      # Database schema and sample data
├── README.md         # Project documentation
├── image/            # Static images
└── myenv/            # Python virtual environment
```

---

## Step-by-Step Setup Guide

### Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **MySQL 8.0+ or MariaDB 10.4+** - [Download MySQL](https://dev.mysql.com/downloads/)
- **Git** (optional) - For version control

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd Data.traffic

# Or manually download and extract the project folder
```

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv myenv

# macOS/Linux
python3 -m venv myenv
```

### Step 3: Activate the Virtual Environment

```bash
# Windows (Command Prompt)
myenv\Scripts\activate.bat

# Windows (PowerShell)
myenv\Scripts\Activate.ps1

# macOS/Linux
source myenv/bin/activate
```

### Step 4: Install Required Dependencies

```bash
pip install fastapi uvicorn mysql-connector-python python-jose[cryptography] passlib[bcrypt] python-multipart pydantic bcrypt
```

Or create a `requirements.txt` file with:
```
fastapi==0.128.0
uvicorn==0.40.0
mysql-connector-python==9.5.0
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.22
pydantic==2.12.5
bcrypt==5.0.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 5: Configure MySQL Database

1. **Start MySQL Server**

2. **Create the Database**
   ```sql
   CREATE DATABASE IF NOT EXISTS customer_portal;
   ```

3. **Import the Schema and Data**
   ```bash
   # Windows
   mysql -u root -p customer_portal < Data.sql.sql

   # Or use MySQL Workbench / HeidiSQL to import
   ```

4. **Create the Users Table** (if not in SQL file)
   ```sql
   USE customer_portal;
   
   CREATE TABLE IF NOT EXISTS users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(100) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL,
       user_display_name VARCHAR(200),
       status TINYINT DEFAULT 1,
       create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Step 6: Update Database Configuration

Edit `database.py` and update the connection settings:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",  # Set your MySQL password
    "database": "customer_portal",
    "port": 3306  # Default MySQL port (change if needed)
}
```

### Step 7: Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 8: Access the API

- **API Root**: http://localhost:8000/
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

---

## Configuration

### Environment Variables (Recommended for Production)

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secure-random-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=customer_portal
DB_PORT=3306
```

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint     | Description                    | Auth Required |
|--------|--------------|--------------------------------|---------------|
| POST   | `/register`  | Register a new user            | No            |
| POST   | `/login`     | Login and get JWT token        | No            |
| POST   | `/logout`    | Logout (client-side)           | No            |

### Traffic Data Endpoints

| Method | Endpoint                  | Description                           | Auth Required |
|--------|---------------------------|---------------------------------------|---------------|
| GET    | `/`                       | API health check                      | No            |
| POST   | `/traffic/summary`        | Get traffic data by WAN IP and time   | Yes           |
| POST   | `/traffic/dashboard-summary` | Get aggregated traffic by location | Yes           |
| POST   | `/user/activity-history`  | Get user access history by WAN IP     | Yes           |

### Example API Requests

#### Register User
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123", "confirm_password": "secret123", "user_display_name": "John Doe"}'
```

#### Login
```bash
curl -X POST http://localhost:8000/login \
  -d "username=john&password=secret123"
```

#### Get Traffic Summary (with token)
```bash
curl -X POST http://localhost:8000/traffic/summary \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"wan_ip": "10.249.12.86", "from_time": "2026-01-01 00:00:00", "to_time": "2026-01-31 23:59:59"}'
```

---

## Known Issues & Recommendations

### Security Issues (High Priority)

1. **Hardcoded Secret Key** (`auth.py`)
   - **Issue**: `SECRET_KEY = "mysecretkey"` is a weak, hardcoded secret
   - **Fix**: Use environment variables with a strong random key
   ```python
   import os
   SECRET_KEY = os.getenv("SECRET_KEY", "fallback-development-only-key")
   ```

2. **Plain Text Password Support** (`auth.py`)
   - **Issue**: `verify_password()` allows plain text password comparison
   - **Risk**: Passwords stored in plain text can be compromised
   - **Fix**: Always hash passwords and remove plain text comparison

3. **Passwords Not Hashed on Registration** (`database.py`)
   - **Issue**: `create_user()` stores passwords without hashing
   - **Fix**: Import and use `get_password_hash()` from auth.py
   ```python
   from auth import get_password_hash
   hashed_pw = get_password_hash(password)
   ```

4. **Empty Database Password** (`database.py`)
   - **Issue**: Default empty password: `"password": ""`
   - **Fix**: Set a strong database password in production

### Code Quality Issues

5. **Unused Function** (`auth.py`)
   - `logout_user()` is defined but never called

6. **Type Inconsistency** (`models.py`)
   - `UserActivityFilter.from_time/to_time` are `datetime` but used as strings in queries

7. **No Pagination**
   - Large datasets could cause performance issues
   - **Recommendation**: Add `limit` and `offset` parameters

8. **File Naming**
   - `Data.sql.sql` has duplicate extension - rename to `schema.sql`

### Recommendations for Production

- Use environment variables for all secrets
- Implement rate limiting (e.g., `slowapi`)
- Add request logging
- Implement token blacklisting for proper logout
- Add database connection pooling
- Use HTTPS in production
- Add input sanitization for SQL injection prevention

---

## License

This project is provided as-is for educational and development purposes.
