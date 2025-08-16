// Custom Cypress commands

// Command to get element by data-cy attribute
Cypress.Commands.add('getByCy', (selector) => {
  return cy.get(`[data-cy=${selector}]`)
})

// Command to check if element contains text
Cypress.Commands.add('containsText', { prevSubject: 'element' }, (subject, text) => {
  return cy.wrap(subject).should('contain.text', text)
})

// Command to wait for element to be visible
Cypress.Commands.add('waitForVisible', (selector, timeout = 10000) => {
  return cy.get(selector, { timeout }).should('be.visible')
})

// Command to simulate typing with delay
Cypress.Commands.add('typeSlowly', { prevSubject: 'element' }, (subject, text, delay = 100) => {
  return cy.wrap(subject).type(text, { delay })
})

// Add TypeScript support for custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      getByCy(selector: string): Chainable<JQuery<HTMLElement>>
      containsText(text: string): Chainable<JQuery<HTMLElement>>
      waitForVisible(selector: string, timeout?: number): Chainable<JQuery<HTMLElement>>
      typeSlowly(text: string, delay?: number): Chainable<JQuery<HTMLElement>>
      login(email?: string, password?: string): Chainable<void>
      logout(): Chainable<void>
      apiRequest(method: string, url: string, body?: any, headers?: object): Chainable<any>
      waitForApi(): Chainable<any>
    }
  }
}