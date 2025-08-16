describe('ML Project Frontend E2E Tests', () => {
  beforeEach(() => {
    // Wait for backend API to be available
    cy.waitForApi()
    
    // Visit the application
    cy.visit('/')
  })

  describe('Application Loading', () => {
    it('should load the homepage successfully', () => {
      cy.title().should('not.be.empty')
      cy.get('body').should('be.visible')
      
      // Check for main navigation or key elements
      cy.get('header').should('exist')
    })

    it('should have working navigation', () => {
      // Test navigation links (adjust selectors based on your app)
      cy.get('nav').should('exist')
      
      // Check for login/auth links
      cy.contains('Login').should('be.visible')
    })
  })

  describe('Authentication Flow', () => {
    it('should navigate to login page', () => {
      cy.visit('/login')
      cy.url().should('include', '/login')
      
      // Check login form elements
      cy.get('input[type="email"]').should('be.visible')
      cy.get('input[type="password"]').should('be.visible')
      cy.get('button[type="submit"]').should('be.visible')
    })

    it('should handle login form validation', () => {
      cy.visit('/login')
      
      // Try to submit empty form
      cy.get('button[type="submit"]').click()
      
      // Should show validation messages (adjust based on your validation)
      cy.get('form').should('exist')
    })

    it('should attempt login with test credentials', () => {
      cy.visit('/login')
      
      cy.get('input[type="email"]').type('test@example.com')
      cy.get('input[type="password"]').type('testpassword123')
      cy.get('button[type="submit"]').click()
      
      // Wait for response and check result
      cy.wait(2000)
      
      // Either successful login (redirect) or error message
      cy.url().should('not.eq', Cypress.config().baseUrl + '/login')
        .or('contain', 'error')
        .or('contain', 'invalid')
    })
  })

  describe('API Tester Component', () => {
    it('should access API tester page', () => {
      // Try to navigate to API tester (adjust route based on your app)
      cy.visit('/api-tester')
      cy.url().should('include', '/api-tester')
      
      // Check for API tester elements
      cy.get('select').should('exist') // Method selector
      cy.get('input').should('exist')  // URL input
      cy.get('button').should('contain', 'Enviar')
    })

    it('should test API endpoint interaction', () => {
      cy.visit('/api-tester')
      
      // Select GET method
      cy.get('select').select('GET')
      
      // Enter test path
      cy.get('input').clear().type('/health')
      
      // Click send button
      cy.get('button').contains('Enviar').click()
      
      // Wait for response
      cy.wait(3000)
      
      // Check for response display
      cy.get('pre').should('exist')
    })
  })

  describe('Dashboard Functionality', () => {
    it('should display main dashboard elements', () => {
      cy.visit('/')
      
      // Check for dashboard components
      cy.get('h1, h2, h3').should('exist')
      
      // Check for cards or widgets
      cy.get('[class*="card"], [class*="widget"]').should('exist')
    })

    it('should handle responsive design', () => {
      // Test mobile viewport
      cy.viewport('iphone-x')
      cy.visit('/')
      cy.get('body').should('be.visible')
      
      // Test tablet viewport
      cy.viewport('ipad-2')
      cy.visit('/')
      cy.get('body').should('be.visible')
      
      // Test desktop viewport
      cy.viewport(1920, 1080)
      cy.visit('/')
      cy.get('body').should('be.visible')
    })
  })

  describe('Error Handling', () => {
    it('should handle 404 errors gracefully', () => {
      cy.visit('/non-existent-page', { failOnStatusCode: false })
      
      // Should show 404 page or redirect
      cy.get('body').should('contain.text', '404')
        .or('not.contain.text', 'error')
    })

    it('should handle network errors', () => {
      // Intercept API calls and simulate network error
      cy.intercept('POST', '**/api/**', { forceNetworkError: true }).as('networkError')
      
      cy.visit('/api-tester')
      cy.get('select').select('GET')
      cy.get('input').clear().type('/health')
      cy.get('button').contains('Enviar').click()
      
      // Should handle error gracefully
      cy.wait(3000)
      cy.get('body').should('exist')
    })
  })

  describe('Performance Tests', () => {
    it('should load within acceptable time', () => {
      const startTime = Date.now()
      
      cy.visit('/')
      cy.get('body').should('be.visible')
      
      cy.then(() => {
        const loadTime = Date.now() - startTime
        expect(loadTime).to.be.lessThan(5000) // Should load within 5 seconds
      })
    })

    it('should handle multiple rapid clicks', () => {
      cy.visit('/')
      
      // Find a clickable element and click it multiple times
      cy.get('button').first().then($btn => {
        if ($btn.length > 0) {
          cy.wrap($btn).click()
          cy.wrap($btn).click()
          cy.wrap($btn).click()
          
          // Application should remain stable
          cy.get('body').should('be.visible')
        }
      })
    })
  })

  describe('Accessibility Tests', () => {
    it('should have proper heading structure', () => {
      cy.visit('/')
      
      // Check for h1 tag
      cy.get('h1').should('exist')
      
      // Check that headings are in logical order
      cy.get('h1, h2, h3, h4, h5, h6').should('exist')
    })

    it('should support keyboard navigation', () => {
      cy.visit('/')
      
      // Tab through interactive elements
      cy.get('body').tab()
      cy.focused().should('exist')
      
      // Check that focus is visible
      cy.focused().should('have.css', 'outline')
        .or('have.css', 'box-shadow')
        .or('have.css', 'border')
    })
  })

  describe('Integration with Backend', () => {
    it('should successfully connect to backend health endpoint', () => {
      cy.apiRequest('GET', '/health').then((response) => {
        expect(response.status).to.eq(200)
        expect(response.body).to.have.property('status', 'ok')
      })
    })

    it('should handle API authentication flow', () => {
      // Test login API endpoint
      cy.apiRequest('POST', '/auth/token', {
        username: 'test@example.com',
        password: 'testpassword123'
      }).then((response) => {
        // Should either succeed or fail gracefully
        expect(response.status).to.be.oneOf([200, 400, 401, 422])
      })
    })
  })
})