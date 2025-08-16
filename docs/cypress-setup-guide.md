# Cypress E2E Testing Setup Guide

## Overview
This guide explains how to set up and run Cypress end-to-end tests for the ML Project frontend.

## Prerequisites
- Node.js 18+ installed
- Frontend application running on localhost:3000 (or configured port)
- Backend API running on localhost:8000 (or configured port)

## Installation

Cypress is already configured in the project. To install dependencies:

```bash
cd frontend
npm install
npx cypress install
```

## Configuration

Cypress configuration is in `frontend/cypress.config.js`:

```javascript
{
  "e2e": {
    "baseUrl": "http://localhost:3000",
    "supportFile": "cypress/support/e2e.js",
    "specPattern": "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    "video": true,
    "screenshotOnRunFailure": true,
    "defaultCommandTimeout": 10000,
    "env": {
      "BACKEND_URL": "http://localhost:8000"
    }
  }
}
```

## Running Tests

### Interactive Mode (Development)
```bash
cd frontend
npm run cypress:open
```

### Headless Mode (CI/CD)
```bash
cd frontend
npm run cypress:run
# or
npm run e2e
```

### With Custom Configuration
```bash
cd frontend
npx cypress run --headless --browser chrome
```

## Test Structure

### Test Files Location
- Tests: `frontend/cypress/e2e/*.cy.js`
- Support: `frontend/cypress/support/`
- Fixtures: `frontend/cypress/fixtures/`

### Custom Commands
Located in `frontend/cypress/support/commands.js`:

```javascript
// Get element by data-cy attribute
cy.getByCy('login-button')

// Login helper
cy.login('test@example.com', 'password123')

// API request helper
cy.apiRequest('GET', '/health')

// Wait for API to be ready
cy.waitForApi()
```

## Writing Tests

### Basic Test Example
```javascript
describe('Application Tests', () => {
  beforeEach(() => {
    cy.waitForApi()
    cy.visit('/')
  })

  it('should load homepage', () => {
    cy.title().should('not.be.empty')
    cy.get('body').should('be.visible')
  })

  it('should navigate to login', () => {
    cy.visit('/login')
    cy.url().should('include', '/login')
    cy.get('input[type="email"]').should('be.visible')
  })
})
```

### Authentication Test
```javascript
it('should login successfully', () => {
  cy.visit('/login')
  cy.get('input[type="email"]').type('test@example.com')
  cy.get('input[type="password"]').type('testpassword123')
  cy.get('button[type="submit"]').click()
  
  cy.url().should('not.include', '/login')
  cy.window().its('localStorage.access_token').should('exist')
})
```

### API Integration Test
```javascript
it('should test API endpoint', () => {
  cy.apiRequest('GET', '/health').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('status', 'ok')
  })
})
```

## Best Practices

### 1. Use Data Attributes
Add `data-cy` attributes to elements for reliable selection:

```jsx
<button data-cy="login-button">Login</button>
<input data-cy="email-input" type="email" />
```

```javascript
cy.getByCy('login-button').click()
```

### 2. Wait for API Responses
```javascript
cy.intercept('POST', '/api/login').as('loginRequest')
cy.get('[data-cy=login-button]').click()
cy.wait('@loginRequest')
```

### 3. Use Page Objects
Create reusable page objects:

```javascript
class LoginPage {
  visit() {
    cy.visit('/login')
  }
  
  fillEmail(email) {
    cy.getByCy('email-input').type(email)
    return this
  }
  
  fillPassword(password) {
    cy.getByCy('password-input').type(password)
    return this
  }
  
  submit() {
    cy.getByCy('login-button').click()
    return this
  }
}
```

### 4. Test Data Management
Use fixtures for test data:

```javascript
cy.fixture('example').then((data) => {
  cy.get('[data-cy=email-input]').type(data.user.email)
})
```

## CI/CD Integration

The CI/CD pipeline automatically:

1. **Installs Dependencies**: `npm ci` and `npx cypress install`
2. **Starts Services**: Backend API and frontend application
3. **Runs Tests**: `npx cypress run --headless --browser chrome`
4. **Captures Artifacts**: Screenshots and videos on failure

### Environment Configuration
Tests run with these environment variables:
- `CYPRESS_BASE_URL`: Frontend application URL
- `CYPRESS_BACKEND_URL`: Backend API URL

## Debugging

### 1. Interactive Mode
Run `npm run cypress:open` to debug tests interactively

### 2. Screenshots and Videos
Failed tests automatically capture:
- Screenshots: `cypress/screenshots/`
- Videos: `cypress/videos/`

### 3. Console Logs
View browser console in Cypress UI or add debug commands:

```javascript
cy.window().then((win) => {
  console.log(win.localStorage)
})
```

### 4. Network Debugging
Monitor network requests:

```javascript
cy.intercept('**').as('allRequests')
cy.visit('/')
cy.get('@allRequests.all').should('have.length.greaterThan', 0)
```

## Common Issues

### 1. Application Not Loading
- Verify frontend server is running
- Check `baseUrl` in configuration
- Ensure no CORS issues

### 2. API Connection Issues
- Verify backend server is running
- Check `BACKEND_URL` environment variable
- Test API endpoints manually

### 3. Flaky Tests
- Add appropriate waits: `cy.wait()` or `cy.intercept()`
- Use `cy.should()` for assertions
- Avoid fixed timeouts

### 4. Element Not Found
- Use `data-cy` attributes
- Check element visibility timing
- Add explicit waits

## Performance Considerations

### 1. Test Parallelization
Run tests in parallel for faster execution:

```bash
npx cypress run --record --parallel
```

### 2. Smart Test Selection
Group related tests and run subsets:

```bash
npx cypress run --spec "cypress/e2e/auth/*.cy.js"
```

### 3. Resource Cleanup
Clear state between tests:

```javascript
beforeEach(() => {
  cy.clearLocalStorage()
  cy.clearCookies()
})
```

## Extending Tests

### 1. Add New Test Suites
Create new `.cy.js` files in `cypress/e2e/`

### 2. Custom Commands
Add reusable commands in `cypress/support/commands.js`

### 3. Plugins
Install Cypress plugins for additional functionality:

```bash
npm install --save-dev @cypress/code-coverage
npm install --save-dev cypress-axe  # Accessibility testing
```

## Accessibility Testing

Add accessibility tests using cypress-axe:

```javascript
it('should not have accessibility violations', () => {
  cy.visit('/')
  cy.injectAxe()
  cy.checkA11y()
})
```

## Visual Testing

Add visual regression testing:

```javascript
it('should match visual snapshot', () => {
  cy.visit('/')
  cy.matchImageSnapshot('homepage')
})
```