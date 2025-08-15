# 🧪 Integration Tests Documentation

## Overview

This document describes how to run the comprehensive integration tests implemented for the ML Project backend. The tests cover OAuth authentication, database operations, and external API integration with Mercado Libre.

## Test Structure

```
backend/tests/integration/
├── __init__.py                          # Package initialization
├── conftest.py                          # Test configuration and fixtures
├── test_oauth_integration.py            # OAuth flow tests
├── test_database_integration.py         # Database operation tests
├── test_product_management.py           # Product CRUD tests
└── test_communication_integration.py    # End-to-end communication tests
```

## Test Categories

### 1. OAuth Integration Tests (`test_oauth_integration.py`)
- **PKCE Flow**: Tests code verifier/challenge generation and authorization URL building
- **Database Integration**: Tests OAuth session and token persistence
- **Token Exchange**: Tests authorization code to access token exchange
- **Mercado Libre API**: Tests user info, products, and categories retrieval
- **Endpoint Integration**: Tests OAuth endpoints with database
- **Refresh Token**: Tests token refresh functionality

### 2. Database Integration Tests (`test_database_integration.py`)
- **Connection**: Tests database connection and transaction handling
- **User Model**: Tests user CRUD operations and constraints
- **OAuth Token Model**: Tests token storage and relationships
- **OAuth Session Model**: Tests session management
- **Performance**: Tests bulk operations and complex queries
- **Data Integrity**: Tests constraints and validation
- **Migration**: Tests schema compatibility

### 3. Product Management Tests (`test_product_management.py`)
- **Creation Flow**: Tests complete product creation workflow
- **Querying Flow**: Tests product listing and filtering
- **Update Flow**: Tests product modifications and status changes
- **Deletion Flow**: Tests product removal
- **End-to-End**: Tests complete product lifecycle

### 4. Communication Integration Tests (`test_communication_integration.py`)
- **Full System**: Tests complete OAuth to product management flow
- **Error Handling**: Tests error propagation across components
- **Data Consistency**: Tests data synchronization
- **Performance**: Tests system behavior under load
- **End-to-End Scenarios**: Tests realistic user journeys

## Running Tests

### Prerequisites

1. **Python Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   - **Local Development**: Tests use SQLite by default
   - **CI/Production**: Tests use PostgreSQL

### Local Development (SQLite)

Run all integration tests:
```bash
cd backend
python -m pytest tests/integration/ -v
```

Run specific test categories:
```bash
# OAuth tests only
python -m pytest tests/integration/test_oauth_integration.py -v

# Database tests only
python -m pytest tests/integration/test_database_integration.py -v

# Product management tests only
python -m pytest tests/integration/test_product_management.py -v

# Communication tests only
python -m pytest tests/integration/test_communication_integration.py -v
```

Run specific test classes:
```bash
# OAuth PKCE tests
python -m pytest tests/integration/test_oauth_integration.py::TestOAuthPKCEFlow -v

# Database connection tests
python -m pytest tests/integration/test_database_integration.py::TestDatabaseConnection -v
```

### CI Environment (PostgreSQL)

The CI workflow automatically sets up PostgreSQL and runs tests. The database configuration is handled via environment variables:

```yaml
DATABASE_URL=postgresql+psycopg2://test_user:test_password@localhost:5432/test_db
```

### Manual PostgreSQL Setup

To run tests with PostgreSQL locally:

1. **Start PostgreSQL**:
   ```bash
   docker run --name test-postgres -e POSTGRES_USER=test_user -e POSTGRES_PASSWORD=test_password -e POSTGRES_DB=test_db -p 5432:5432 -d postgres:15
   ```

2. **Set Environment Variables**:
   ```bash
   export DATABASE_URL=postgresql+psycopg2://test_user:test_password@localhost:5432/test_db
   export USE_POSTGRES=1
   ```

3. **Run Tests**:
   ```bash
   python -m pytest tests/integration/ -v
   ```

## Test Coverage

Run tests with coverage reporting:
```bash
cd backend
python -m pytest tests/integration/ --cov=app --cov-report=term-missing --cov-report=html
```

## Environment Variables

The tests support the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | SQLite for local, PostgreSQL for CI |
| `USE_POSTGRES` | Force PostgreSQL usage | `false` |
| `CI` | CI environment flag | `false` |
| `ML_CLIENT_ID` | Mercado Libre client ID | `test_client_id` |
| `ML_CLIENT_SECRET` | Mercado Libre client secret | `test_client_secret` |
| `SECRET_KEY` | JWT secret key | `test_secret_key_for_testing_only` |

## Test Fixtures

### Database Fixtures
- `pg_session`: Database session (SQLite or PostgreSQL)
- `pg_client`: FastAPI test client with database
- `pg_async_client`: Async HTTP client for API calls
- `pg_test_user`: Test user with authentication
- `pg_test_admin_user`: Test admin user
- `oauth_session_data`: OAuth session for testing
- `oauth_token_data`: OAuth token for testing

### Mock Data Fixtures
- `mock_ml_token`: Mock Mercado Libre token response
- `mock_ml_user_info`: Mock user information from ML API
- `mock_ml_products`: Mock product data from ML API
- `mock_ml_categories`: Mock category data from ML API

### Authentication Fixtures
- `pg_access_token`: JWT access token for test user
- `pg_admin_access_token`: JWT access token for admin user
- `pg_auth_headers`: Authorization headers for API calls
- `pg_admin_auth_headers`: Admin authorization headers

## Mocking Strategy

The tests use comprehensive mocking for external API calls to:
- Ensure tests are deterministic and fast
- Avoid dependencies on external services
- Test error scenarios safely
- Simulate various API responses

Mock patterns used:
```python
# HTTP client mocking
with patch("httpx.AsyncClient.get") as mock_get:
    mock_response = MagicMock()
    mock_response.json.return_value = expected_data
    mock_get.return_value = mock_response
    
    result = await api_function()
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - Check DATABASE_URL environment variable
   - Verify database credentials

2. **Import Errors**:
   - Ensure all dependencies are installed
   - Check PYTHONPATH includes backend directory

3. **Authentication Errors**:
   - Verify SECRET_KEY is set
   - Check JWT token generation

4. **Permission Errors**:
   - Ensure proper file permissions
   - Check database write permissions

### Debug Mode

Run tests with debug output:
```bash
python -m pytest tests/integration/ -v -s --tb=long
```

## Contributing

When adding new integration tests:

1. **Follow naming conventions**: `test_<functionality>_<scenario>`
2. **Use appropriate fixtures**: Reuse existing fixtures when possible
3. **Mock external calls**: Always mock HTTP requests to external APIs
4. **Test error scenarios**: Include negative test cases
5. **Document test purpose**: Add docstrings explaining test objectives
6. **Maintain isolation**: Ensure tests don't depend on each other

## Performance Considerations

- Tests are designed to run quickly (< 30 seconds for full suite)
- Database operations use transactions for fast cleanup
- External API calls are mocked to avoid network delays
- Bulk operations are tested for performance characteristics

## Security Notes

- Test data uses non-production credentials
- Sensitive data is mocked or anonymized
- Tests verify security constraints (authentication, authorization)
- Token validation and expiration are tested