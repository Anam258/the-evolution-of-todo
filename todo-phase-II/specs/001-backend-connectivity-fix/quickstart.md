# Quickstart Guide: Backend Connectivity and Startup Fixes

## Overview
This guide provides instructions for setting up and running the backend service after applying fixes for connectivity and startup issues.

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL database
- Properly configured .env file

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd todo-phase-II
cd backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
# python-dotenv should now be included in requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and update with your values:
```bash
cp .env.example .env
# Edit .env to update DATABASE_URL and BETTER_AUTH_SECRET
```

Required environment variables:
- `BETTER_AUTH_SECRET`: At least 32-character secret for JWT signing
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Port to run the server on (default: 8000)

### 4. Run the Application
```bash
# Option 1: Using uvicorn directly
uvicorn src.main:app --reload --port 8000

# Option 2: Running the main module
python -m src.main

# Option 3: Using python directly
python src/main.py
```

## Verification Steps

### 1. Check Backend Startup
After starting the application, you should see:
- No environment variable errors
- Successful database connection (if available)
- Server listening on the configured port

### 2. Test Health Endpoints
Once the server is running, verify the health endpoints:
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/monitoring/health
```

Expected responses:
- `/health` should return: `{"status": "healthy", "service": "todo-api"}`
- `/monitoring/health` should return detailed health status

### 3. Check for Error Logs
Monitor the console output for any ValueError or PermissionError related to:
- Environment variables
- Port binding
- Database connections

## Troubleshooting

### Port Conflict Errors
If you get port binding errors:
1. Check if another process is using the configured port:
   ```bash
   netstat -ano | findstr :8000  # Windows
   lsof -i :8000                 # macOS/Linux
   ```
2. Change the PORT in your .env file to an available port
3. Restart the application

### Environment Variable Issues
If you encounter BETTER_AUTH_SECRET errors:
1. Verify the variable is present in your .env file
2. Ensure the secret is at least 32 characters long
3. Check that python-dotenv is properly installed and imported
4. Verify the .env file is in the correct directory (backend/)

### Permission Errors
On Windows, if you encounter WinError 10013:
1. Run your terminal/command prompt as Administrator
2. Or choose a different port in your .env file
3. Ensure no firewall is blocking the port

### Missing Dependencies
If you encounter import errors:
1. Make sure you've installed all dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Verify that python-dotenv is installed (it's now included in requirements.txt)

### Authentication Configuration Errors
If authentication configuration fails:
1. Check that BETTER_AUTH_SECRET is properly set in .env file
2. Verify the secret is at least 32 characters long
3. If the .env file is missing, the system will generate a temporary secret for development,
   but this should not be used in production

### Logging and Diagnostics
The system now includes enhanced logging for startup issues:
- Environment variable loading is logged
- Authentication configuration validation is logged
- Port binding attempts are logged with fallback information

## Expected Outcomes
After applying the fixes:
- Backend service starts without environment variable errors (100% of attempts)
- All required environment variables are accessible within 5 seconds of startup
- Health check endpoints return successful 200 OK responses
- Port binding succeeds without conflicts (100% of startup attempts)
- No ValueError or PermissionError related to environment variables or port binding in logs