// Cypress support commands and configuration

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Configure Cypress behavior
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test on uncaught exceptions
  // This is useful for applications that might have expected console errors
  if (err.message.includes('ResizeObserver loop limit exceeded')) {
    return false
  }
  if (err.message.includes('Non-Error promise rejection captured')) {
    return false
  }
  return true
})

// Set up global hooks
beforeEach(() => {
  // Clear local storage before each test
  cy.clearLocalStorage()
  
  // Set default viewport
  cy.viewport(1280, 720)
})

// Custom commands for authentication
Cypress.Commands.add('login', (email = 'test@example.com', password = 'testpassword123') => {
  cy.visit('/login')
  cy.get('[data-cy=email-input]').type(email)
  cy.get('[data-cy=password-input]').type(password)
  cy.get('[data-cy=login-button]').click()
  
  // Wait for successful login (adjust selector based on your app)
  cy.url().should('not.include', '/login')
  cy.window().its('localStorage.access_token').should('exist')
})

Cypress.Commands.add('logout', () => {
  cy.clearLocalStorage()
  cy.visit('/login')
})

// API testing helpers
Cypress.Commands.add('apiRequest', (method, url, body = null, headers = {}) => {
  const baseUrl = Cypress.env('BACKEND_URL') || 'http://localhost:8000'
  
  return cy.request({
    method,
    url: `${baseUrl}${url}`,
    body,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    failOnStatusCode: false
  })
})

// Wait for API to be ready
Cypress.Commands.add('waitForApi', () => {
  const baseUrl = Cypress.env('BACKEND_URL') || 'http://localhost:8000'
  cy.request({
    url: `${baseUrl}/health`,
    retryOnStatusCodeFailure: true,
    timeout: 30000
  }).its('status').should('eq', 200)
})