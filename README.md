# Enterprise Automation Platform

A modern automation platform with AI integration, LDAP authentication, and a beautiful UI.

## Features

- 🤖 **AI-Powered Automation**: Natural language task processing with OpenAI/Anthropic
- 🔐 **Enterprise Authentication**: LDAP integration + JWT tokens
- 📊 **Modern Dashboard**: React + Material-UI interface
- ⚡ **Async Task Execution**: Celery + Redis for background jobs
- 🗄️ **Flexible Database**: MongoDB or MySQL support
- 🐳 **Docker Ready**: Easy containerization and deployment
- 📝 **Workflow Builder**: Create and schedule automation tasks
- 📈 **Real-time Monitoring**: Track task execution and logs

## Tech Stack

### Backend
- Python 3.11+
- FastAPI (REST API)
- Celery + Redis (Task Queue)
- SQLAlchemy / Motor (Database ORMs)
- python-ldap (Authentication)
- LangChain (AI Integration)

### Frontend
- React 18
- Material-UI (MUI)
- Axios (API Client)
- React Router
- Context API (State Management)

### Database
- MongoDB (Default)
- MySQL (Alternative)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis Server
- MongoDB or MySQL
- LDAP Server (optional for testing)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python -m app.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Docker Deployment (Future)

```bash
docker-compose up -d
```

## Project Structure

```
automation-platform/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Configuration & security
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── automation/  # Automation engine
│   │   └── main.py      # Application entry point
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── App.jsx
│   └── package.json
├── docker/              # Docker configurations
└── docs/                # Documentation
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME=Automation Platform
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_TYPE=mongodb  # or mysql
MONGODB_URL=mongodb://localhost:27017/automation
MYSQL_URL=mysql://user:pass@localhost/automation

# Redis
REDIS_URL=redis://localhost:6379/0

# LDAP
LDAP_SERVER=ldap://your-ldap-server
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=ou=users,dc=example,dc=com
LDAP_BIND_USER=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=your-password

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# JWT
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Usage

### Creating an Automation Task

1. Login to the dashboard
2. Navigate to "Tasks" → "Create New"
3. Define your automation (Python script, API call, etc.)
4. Schedule or run immediately
5. Monitor execution in real-time

### AI-Assisted Automation

Use natural language to create tasks:
```
"Send me an email report of server CPU usage every morning at 9 AM"
```

The AI will generate the appropriate automation workflow.

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
