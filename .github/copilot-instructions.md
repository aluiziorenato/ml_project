# ML Project - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

This is a comprehensive ML automation system for Mercado Libre with multiple components:
- **Backend (FastAPI)**: Main application with OAuth integration, database models, and REST APIs
- **Frontend (React)**: Vite-based single-page application 
- **ML Automation Services**: Three independent microservices for campaign simulation, learning, and optimization
- **Infrastructure**: Docker Compose orchestration with PostgreSQL and pgAdmin

## Critical Setup Requirements

**NEVER CANCEL builds or long-running commands**. All build times documented below include safety margins.

### Environment Setup

**ALWAYS** set up the environment in this exact order:

1. **Backend Dependencies** (NEVER CANCEL - takes 2 minutes, timeout 180 seconds):
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env to set required values:
   # DATABASE_URL=sqlite:///./test.db (for local testing)
   # SECRET_KEY=your-secret-key
   # ADMIN_PASSWORD=your-admin-password
   ```

3. **Frontend Dependencies** (NEVER CANCEL - takes 1 minute, timeout 120 seconds):
   ```bash
   cd frontend
   npm install
   # Fix permissions if needed:
   chmod +x node_modules/.bin/vite
   ```

## Build and Test Commands

### Backend Operations

**Run Tests** (NEVER CANCEL - takes 2 minutes, timeout 180 seconds):
```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

**Run Regression Tests** (NEVER CANCEL - takes 1 minute, timeout 120 seconds):
```bash
cd backend  
source .venv/bin/activate
python -m pytest tests/regression/ -v
```

**Start Backend Server**:
```bash
cd backend
source .venv/bin/activate
ADMIN_PASSWORD=your-admin-password uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Operations

**Build Frontend** (NEVER CANCEL - takes 1 minute, timeout 120 seconds):
```bash
cd frontend
npm run build
```

**Start Frontend Development Server**:
```bash
cd frontend
npm run dev
```

### ML Automation Services

Each service runs independently on ports 8001, 8002, 8003.

**Start Simulator Service (Port 8001)**:
```bash
cd simulator_service
python3 -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Start Learning Service (Port 8002)**:
```bash
cd learning_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**Start Optimizer Service (Port 8003)**:
```bash
cd optimizer_ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Docker Operations

### Core Stack with Docker Compose

**IMPORTANT**: The main docker-compose.yml includes only the core stack (backend, frontend, database, pgAdmin). The ML automation services run separately.

**CRITICAL**: Docker Compose operations can take significant time on first run.

**Start Core Stack** (NEVER CANCEL - first build takes 10 minutes, timeout 900 seconds):
```bash
docker compose up --build -d
```

**Subsequent Builds** (NEVER CANCEL - takes 3 minutes, timeout 300 seconds):
```bash
docker compose up --build -d
```

### Individual ML Service Builds

The ML automation services (simulator, learning, optimizer) are not included in docker-compose.yml and must be built/run separately.

**Build Single Service** (NEVER CANCEL - takes 2 minutes, timeout 180 seconds):
```bash
# Simulator Service
cd simulator_service
docker build -t simulator-service:latest .
docker run -p 8001:8001 simulator-service:latest

# Learning Service  
cd learning_service
docker build -t learning-service:latest .
docker run -p 8002:8002 learning-service:latest

# Optimizer AI
cd optimizer_ai
docker build -t optimizer-ai:latest .
docker run -p 8003:8003 optimizer-ai:latest
```

**Stop All Services**:
```bash
docker compose down
```

**View Service Status**:
```bash
docker compose ps
```

**View Service Logs**:
```bash
docker compose logs [service-name]
# Example: docker compose logs backend
```

## Validation and Testing

### Health Check Endpoints

**ALWAYS** validate services are running with these health checks:

```bash
# Core Stack (via Docker Compose)
# Backend
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}

# Frontend (check HTML loads)
curl -s http://localhost:3000 | head -5

# ML Services (when running separately)
# Simulator Service  
curl -s http://localhost:8001/health
# Expected: {"status":"healthy","service":"simulator_service"}

# Learning Service
curl -s http://localhost:8002/health  
# Expected: {"status":"healthy","service":"learning_service"}

# Optimizer Service
curl -s http://localhost:8003/health
# Expected: {"status":"healthy","service":"optimizer_ai"}
```

**Note**: ML automation services health endpoints are only available when those services are running separately.

### Manual Validation Scenarios

**ALWAYS** run these validation scenarios after making changes:

1. **Backend API Test**:
   ```bash
   # Test authentication endpoint
   curl -X POST http://localhost:8000/api/auth/register \
   -H "Content-Type: application/json" \
   -d '{"email":"test@example.com","password":"testpass123"}'
   ```

2. **ML Service API Test** (requires service to be running separately):
   ```bash
   # First start the simulator service:
   cd simulator_service && source .venv/bin/activate && uvicorn app.main:app --port 8001
   
   # Then test campaign simulation:
   curl -X POST http://localhost:8001/api/simulate \
   -H "Content-Type: application/json" \
   -d '{
     "product_name": "Test Product",
     "category": "electronics", 
     "budget": 1000.0,
     "duration_days": 14,
     "target_audience": "young_adults",
     "keywords": ["test", "product"]
   }'
   ```

3. **Frontend Accessibility**:
   ```bash
   # Check frontend loads
   curl -s http://localhost:3000 | head -10
   ```

**Note**: ML automation services (ports 8001-8003) are only available when run separately, not through docker-compose.

## Common Issues and Solutions

### Backend Issues

**ImportError: email-validator not installed**
- Solution: Add `email-validator` to requirements.txt and reinstall dependencies

**ValueError: ADMIN_PASSWORD não definido**  
- Solution: Set ADMIN_PASSWORD environment variable explicitly:
  ```bash
  ADMIN_PASSWORD=your-password uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

**Async test failures**
- Solution: Install pytest-asyncio: `pip install pytest-asyncio`

### Frontend Issues

**Permission denied: vite**
- Solution: Fix permissions: `chmod +x node_modules/.bin/vite`

### ML Services Issues

**RuntimeError: Directory 'static' does not exist**
- Solution: Create missing static directories:
  ```bash
  mkdir -p simulator_service/app/static
  mkdir -p learning_service/app/static  
  mkdir -p optimizer_ai/app/static
  ```

**Module import errors in ML services**
- Solution: Ensure you're in the correct directory and virtual environment is activated
- ML services use `app.main:app` module path, not `main:app`

### Docker Issues

**Container startup failures**
- Check logs: `docker compose logs [service-name]`
- Rebuild with no cache: `docker compose build --no-cache`

**Port conflicts**
- Check if ports are already in use: `netstat -tulpn | grep 8000`
- Stop conflicting services or change ports in docker-compose.yml

## Dependencies and Requirements

### Backend Critical Dependencies
- `email-validator` - Email validation for Pydantic models
- `bcrypt` - Secure password hashing  
- `pytest-asyncio` - Async test support
- `python-jose` - JWT token handling
- `sqlmodel` - Database ORM

### Frontend Dependencies
- `react` - Core framework
- `vite` - Build tool and dev server
- `axios` - HTTP client

### Development Tools
- `pytest` - Testing framework
- `pytest-regressions` - Snapshot testing
- `uvicorn` - ASGI server

## Port Configuration

- **8000**: Backend FastAPI application
- **8001**: Simulator Service
- **8002**: Learning Service  
- **8003**: Optimizer AI Service
- **3000**: Frontend React application
- **5432**: PostgreSQL database
- **8080**: pgAdmin interface

## CI/CD Integration

The project includes GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs backend tests (timeout: 300 seconds)
- Runs regression tests (timeout: 300 seconds)  
- Uses Python 3.11
- Requires all tests to pass

**ALWAYS** run local tests before pushing:
```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
python -m pytest tests/regression/ -v
```

## Performance Expectations

**Build Times** (NEVER reduce these timeouts):
- Backend dependency install: ~30 seconds
- Backend tests: ~13 seconds  
- Frontend build: ~5.5 seconds
- Individual Docker build: ~9 seconds
- Full Docker Compose first build: ~38 seconds
- Docker Compose rebuild: ~14 seconds

**CRITICAL**: Always wait for builds to complete. Canceling builds can corrupt the environment.

## Environment Variables Reference

Create `backend/.env` with these values:

```bash
# Database
DATABASE_URL=sqlite:///./test.db
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-strong-password

# Mercado Libre OAuth2  
ML_CLIENT_ID=your-client-id
ML_CLIENT_SECRET=your-client-secret
ML_REDIRECT_URI=http://localhost:8000/api/oauth/callback

# JWT Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256  
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application URLs
APP_BASE_URL=http://localhost:8000
FRONTEND_ORIGIN=http://localhost:3000

# Environment
ENV=development
```

## File Structure Reference

```
├── backend/                 # FastAPI application
│   ├── app/                # Application code
│   │   ├── auth/           # Authentication modules
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # Database models
│   │   └── tests/          # Test suite
│   ├── requirements.txt    # Python dependencies  
│   └── .env               # Environment variables
├── frontend/               # React application
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── dist/              # Built files
├── simulator_service/      # ML campaign simulator
├── learning_service/       # Continuous learning service  
├── optimizer_ai/          # Copywriting optimizer
├── docker-compose.yml     # Service orchestration
└── .github/
    └── workflows/ci.yml   # GitHub Actions
```

## Quick Reference Commands

**Start Core Stack with Docker**:
```bash
docker compose up --build -d
```

**Start Everything Locally** (separate terminals):
```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate && ADMIN_PASSWORD=test123 uvicorn app.main:app --port 8000

# Terminal 2 - Frontend  
cd frontend && npm run dev

# Terminal 3 - Simulator (optional)
cd simulator_service && source .venv/bin/activate && uvicorn app.main:app --port 8001

# Terminal 4 - Learning Service (optional)  
cd learning_service && source .venv/bin/activate && uvicorn app.main:app --port 8002

# Terminal 5 - Optimizer Service (optional)
cd optimizer_ai && source .venv/bin/activate && uvicorn app.main:app --port 8003
```

**Run All Tests**:
```bash
cd backend && source .venv/bin/activate && python -m pytest tests/ -v
```

**Reset Environment**:
```bash
docker compose down
rm -rf backend/.venv frontend/node_modules
# Then re-run setup commands
```