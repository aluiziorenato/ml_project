{
  "e2e": {
    "baseUrl": "http://localhost:3000",
    "supportFile": "cypress/support/e2e.js",
    "specPattern": "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    "video": true,
    "screenshotOnRunFailure": true,
    "defaultCommandTimeout": 10000,
    "requestTimeout": 10000,
    "responseTimeout": 10000,
    "viewportWidth": 1280,
    "viewportHeight": 720,
    "env": {
      "BACKEND_URL": "http://localhost:8000"
    }
  }
}