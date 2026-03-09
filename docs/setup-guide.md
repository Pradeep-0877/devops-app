# Setup Guide

Complete setup instructions for the Automation Platform.

## Prerequisites

### Required Software

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **MongoDB 7.0+**: [Download](https://www.mongodb.com/try/download/community)
- **Redis 7+**: [Download](https://redis.io/download/)

### Optional (for LDAP)

- LDAP Server (Active Directory, OpenLDAP, etc.)

## Installation

### 1. Clone or Download the Project

```bash
cd c:\Users\pradeep.reddy05\Desktop\python-learn
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy the example environment file
copy env.example .env

# Edit .env with your settings
notepad .env
```

**Important Settings:**

```env
# Change these!
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=automation_platform

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# LDAP (optional)
LDAP_ENABLED=False  # Set to True if using LDAP
LDAP_SERVER=ldap://your-server:389
LDAP_BASE_DN=dc=example,dc=com

# AI (optional - add your API key)
OPENAI_API_KEY=sk-your-key-here
AI_PROVIDER=openai
```

### 3. Frontend Setup

```bash
cd ..\frontend
npm install
```

### 4. Start Services

#### Start MongoDB

```bash
# Windows (if MongoDB is installed as a service)
net start MongoDB

# Or run manually
mongod --dbpath C:\data\db
```

#### Start Redis

```bash
# Windows (if Redis is installed)
redis-server

# Or using WSL
wsl redis-server
```

#### Start Backend API

```bash
cd backend
venv\Scripts\activate
python -m app.main
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

#### Start Celery Worker (for background tasks)

Open a new terminal:

```bash
cd backend
venv\Scripts\activate
celery -A app.services.automation_engine.celery_app worker --loglevel=info --pool=solo
```

Note: Windows users must use `--pool=solo` or `--pool=threads`

#### Start Frontend

Open a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

## Testing Your Setup

### 1. Create a Test User

Open your browser to http://localhost:3000

Click on "Register" tab and create a test account:
- Username: testuser
- Email: test@example.com
- Password: Test123!

### 2. Login

Login with your credentials

### 3. Create a Simple Task

1. Click "Create Task"
2. Fill in:
   - Name: "Hello World"
   - Type: Python Script
   - Script:
     ```python
     print("Hello from automation!")
     result = {"message": "Success!"}
     ```
3. Click "Create Task"

### 4. Execute the Task

1. View your task
2. Click "Execute"
3. Check the execution history

## LDAP Configuration (Optional)

If you want to use LDAP authentication:

### 1. Enable LDAP in .env

```env
LDAP_ENABLED=True
LDAP_SERVER=ldap://your-ldap-server:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=ou=users,dc=example,dc=com
LDAP_BIND_USER=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=your-bind-password
LDAP_SEARCH_FILTER=(uid={username})
```

### 2. Test LDAP Connection

Login with an LDAP user's credentials. The system will:
1. Try LDAP authentication first
2. Create a local user record automatically