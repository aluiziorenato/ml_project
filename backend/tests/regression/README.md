# Regression Tests Documentation

## Overview

This document describes the regression testing framework implemented using pytest-regressions for the ML project backend API.

## Structure

The regression tests are organized in the following structure:

```
backend/tests/regression/
├── __init__.py
├── test_api_snapshots.py     # API response regression tests
├── test_model_snapshots.py   # Model/service function regression tests
└── snapshots/                # Stored snapshot data
    ├── test_health_endpoint_snapshot.yml
    ├── test_seo_optimize_snapshot.yml
    └── ... (50+ snapshot files)
```

## Test Categories

### 1. API Snapshots (test_api_snapshots.py)

Tests that capture API response structures and content to detect unintended changes:

- **Health Endpoint**: Basic health check response structure
- **SEO Optimization**: Text optimization API responses with various parameters
- **Categories**: Product category listing and details responses  
- **Authentication**: User registration and token generation responses
- **Error Handling**: Consistent error response structures
- **OAuth**: OAuth flow redirect response structures

### 2. Model Snapshots (test_model_snapshots.py)

Tests that capture business logic outputs from services and models:

- **SEO Service Functions**: Text optimization, keyword extraction, slug generation
- **Mercado Libre Services**: Code generation, URL building for OAuth
- **Data Transformations**: Title optimization, meta description generation
- **Integration Workflows**: Complete end-to-end optimization processes

## Benefits

1. **Regression Detection**: Automatically catches unintended changes in API responses and business logic
2. **Documentation**: Snapshots serve as living documentation of expected outputs
3. **Refactoring Safety**: Enables confident refactoring with immediate feedback on changes
4. **Team Collaboration**: Makes API changes visible and reviewable
5. **Quality Assurance**: Ensures consistency across different environments

## Running Tests

### Run All Regression Tests
```bash
cd backend
pytest tests/regression/ -v
```

### Run Specific Test Categories
```bash
# API snapshots only
pytest tests/regression/test_api_snapshots.py -v

# Model snapshots only  
pytest tests/regression/test_model_snapshots.py -v
```

### Update Snapshots
When changes are intentional, update snapshots using:
```bash
pytest tests/regression/ --regen-all
```

## CI Integration

The regression tests are integrated into the CI pipeline in `.github/workflows/ci.yml`:

```yaml
- name: Run regression tests
  run: |
    cd backend
    pytest tests/regression/ -v
```

This ensures that:
- All pull requests are tested for regressions
- Snapshot changes are visible in code reviews
- Production deployments only happen with passing regression tests

## Test Coverage Areas

The regression tests currently cover:

### API Endpoints
- `/health` - Health check endpoint
- `/api/seo/optimize` - SEO text optimization 
- `/api/categories/` - Product categories listing
- `/api/categories/{id}` - Category details
- `/api/auth/register` - User registration
- `/api/auth/token` - Authentication token generation
- `/api/oauth/login` - OAuth flow initiation

### Service Functions
- `optimize_text()` - Complete SEO optimization workflow
- `generate_code_verifier()` - OAuth PKCE code generation
- `generate_code_challenge()` - OAuth challenge generation  
- `build_authorization_url()` - OAuth URL construction
- `_generate_slug()` - URL slug generation
- `_extract_keywords()` - Keyword extraction from text
- `_optimize_title()` - SEO title optimization
- `_optimize_meta_description()` - Meta description optimization

## Snapshot Management

### Snapshot Files
- Stored in YAML format for human readability
- Automatically generated on first test run
- Updated when running with `--regen-all` flag
- Version controlled to track changes over time

### Best Practices
1. Review snapshot changes carefully in pull requests
2. Only regenerate snapshots when changes are intentional
3. Use descriptive test names that clearly indicate what's being tested
4. Group related tests in logical test classes
5. Include both positive and negative test cases

## Integration with Existing Tests

The regression tests complement the existing test suite:
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Regression Tests**: Test overall behavior consistency
- **E2E Tests**: Test complete user workflows

## Future Enhancements

Potential areas for expansion:
1. **Database State Snapshots**: Capture database state changes
2. **Performance Benchmarks**: Track performance regression over time
3. **Email/Notification Templates**: Snapshot email content templates
4. **Configuration Snapshots**: Track configuration file changes
5. **API Documentation**: Auto-generate API docs from snapshots

## Troubleshooting

### Common Issues

1. **Snapshot Mismatch**: When output changes unexpectedly
   - Review the change to determine if it's intentional
   - Update snapshots if the change is expected
   - Fix the code if the change is a regression

2. **Test Environment Differences**: When tests pass locally but fail in CI
   - Ensure consistent test data and configuration
   - Check for timezone/locale differences
   - Verify dependency versions match

3. **Large Snapshot Files**: When snapshots become too large
   - Consider testing only key fields instead of full responses
   - Split large tests into smaller, focused tests
   - Use data filtering to exclude dynamic fields

### Debug Commands
```bash
# Run with detailed output
pytest tests/regression/ -v -s

# Run specific test with debug info
pytest tests/regression/test_api_snapshots.py::TestAPISnapshots::test_seo_optimize_snapshot -vvv

# Show differences when snapshots don't match
pytest tests/regression/ --tb=short
```