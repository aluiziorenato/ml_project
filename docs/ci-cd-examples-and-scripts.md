# CI/CD Workflow Examples and Scripts

## Backend Integration Test Example

This example shows how to create comprehensive backend integration tests that verify the complete API functionality:

### Example Test: `backend/tests/test_backend_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestBackendIntegration:
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_authentication_flow(self, client, test_user_data):
        """Test complete authentication flow."""
        # Register user
        register_response = client.post("/auth/register", json=test_user_data)
        
        # Login user
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/auth/token", data=login_data)
        
        if login_response.status_code == 200:
            assert "access_token" in login_response.json()
```

### Key Features:
- **PostgreSQL Integration**: Uses real database for testing
- **Authentication Testing**: Complete auth flow validation
- **API Endpoint Testing**: Tests all major endpoints
- **Error Handling**: Graceful error handling and reporting
- **Performance Testing**: Response time validation
- **Sentry Integration**: Error monitoring testing

## Cypress Frontend E2E Test Example

### Example Test: `frontend/cypress/e2e/app.cy.js`

```javascript
describe('ML Project Frontend E2E Tests', () => {
  beforeEach(() => {
    cy.waitForApi()  // Wait for backend API
    cy.visit('/')
  })

  it('should load the homepage successfully', () => {
    cy.title().should('not.be.empty')
    cy.get('body').should('be.visible')
    cy.get('header').should('exist')
  })

  it('should test login flow', () => {
    cy.visit('/login')
    cy.get('input[type="email"]').type('test@example.com')
    cy.get('input[type="password"]').type('testpassword123')
    cy.get('button[type="submit"]').click()
    
    cy.url().should('not.include', '/login')
  })

  it('should test API integration', () => {
    cy.apiRequest('GET', '/health').then((response) => {
      expect(response.status).to.eq(200)
      expect(response.body).to.have.property('status', 'ok')
    })
  })
})
```

### Custom Commands:
```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login')
  cy.get('[data-cy=email-input]').type(email)
  cy.get('[data-cy=password-input]').type(password)
  cy.get('[data-cy=login-button]').click()
})

Cypress.Commands.add('apiRequest', (method, url, body, headers) => {
  const baseUrl = Cypress.env('BACKEND_URL') || 'http://localhost:8000'
  return cy.request({
    method,
    url: `${baseUrl}${url}`,
    body,
    headers: { 'Content-Type': 'application/json', ...headers },
    failOnStatusCode: false
  })
})
```

## Sentry Error Monitoring Setup

### Configuration: `backend/app/monitoring/sentry_config.py`

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from app.settings import settings

def init_sentry():
    if not settings.sentry_dsn:
        return False
    
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
            HttpxIntegration(),
        ],
        before_send=lambda event, hint: add_service_context(event),
    )
    return True

def capture_exception(exception: Exception, **kwargs):
    if settings.sentry_dsn:
        with sentry_sdk.configure_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
```

### Usage in FastAPI:
```python
from app.monitoring.sentry_config import init_sentry, capture_exception

# Initialize Sentry
init_sentry()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    capture_exception(exc, request_path=str(request.url))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

## CI/CD Workflow Structure

### Updated Workflow Jobs:

1. **Lint Jobs** (Parallel)
   - lint-backend
   - lint-frontend
   - lint-modules

2. **Test Jobs** (Parallel)
   - test-backend (unit tests)
   - test-backend-integration (API tests with PostgreSQL)
   - test-frontend (unit tests)
   - test-frontend-cypress (e2e tests)

3. **Security & Build** (Sequential)
   - security-scan
   - build-and-push

4. **Deploy & Coverage** (Sequential)
   - deploy
   - coverage-report

### Job Configuration Examples:

#### Backend Integration Tests Job:
```yaml
test-backend-integration:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:15
      env:
        POSTGRES_PASSWORD: senha
        POSTGRES_USER: usuario
        POSTGRES_DB: nome_do_banco
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
      ports:
        - 5432:5432
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://usuario:senha@localhost:5432/nome_do_banco
        SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
      run: |
        cd backend
        pytest tests/test_backend_integration.py -v --cov=app
```

#### Cypress E2E Tests Job:
```yaml
test-frontend-cypress:
  runs-on: ubuntu-latest
  services:
    postgres: [postgres service config]
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Set up Node.js
      uses: actions/setup-node@v4
    - name: Start backend server
      run: |
        cd backend
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        sleep 10
    - name: Start frontend server
      run: |
        cd frontend
        npm run preview &
        sleep 5
    - name: Run Cypress E2E tests
      env:
        CYPRESS_BASE_URL: http://localhost:4173
        CYPRESS_BACKEND_URL: http://localhost:8000
      run: |
        cd frontend
        npx cypress run --headless --browser chrome
```

## GitHub Secrets Configuration

### Required Secrets:
```
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_password
SECRET_KEY=your_jwt_secret_key
ML_CLIENT_ID=your_mercadolibre_client_id
ML_CLIENT_SECRET=your_mercadolivre_client_secret
```

### Optional Secrets:
```
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## Local Development Setup

### Backend Setup:
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run integration tests
pytest tests/test_backend_integration.py -v

# Run with Sentry (optional)
export SENTRY_DSN="your_sentry_dsn"
uvicorn app.main:app --reload
```

### Frontend Setup:
```bash
cd frontend
npm install
npx cypress install

# Run development server
npm run dev

# Run E2E tests (requires backend running)
npm run cypress:open  # Interactive mode
npm run cypress:run   # Headless mode
```

## Testing Strategy

### Backend Integration Tests:
- **Database Operations**: Create, read, update, delete
- **Authentication Flow**: Registration, login, token validation
- **API Endpoints**: All major endpoints with various scenarios
- **Error Handling**: Invalid inputs, network errors, auth errors
- **Performance**: Response times and concurrent requests
- **External Integrations**: Mocked external API calls

### Frontend E2E Tests:
- **Page Loading**: All major pages load correctly
- **User Interactions**: Forms, buttons, navigation
- **Authentication**: Login/logout flows
- **API Integration**: Frontend-backend communication
- **Responsive Design**: Multiple viewport sizes
- **Error Handling**: Network errors, validation errors
- **Accessibility**: Basic accessibility checks

### Monitoring & Observability:
- **Sentry Integration**: Error tracking and performance monitoring
- **Coverage Reports**: Code coverage for all modules
- **Performance Metrics**: Response times and throughput
- **Health Checks**: Service availability monitoring

## Best Practices

1. **Test Independence**: Each test should be independent and idempotent
2. **Data Cleanup**: Clean up test data after each test
3. **Mocking**: Mock external dependencies in unit tests
4. **Real Integration**: Use real services in integration tests
5. **Error Scenarios**: Test both success and failure cases
6. **Performance**: Include performance assertions
7. **Documentation**: Document test scenarios and expected outcomes
8. **CI/CD Integration**: Ensure tests run reliably in CI environment