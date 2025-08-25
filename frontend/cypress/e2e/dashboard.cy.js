describe('Dashboard', () => {
  it('Carrega métricas em tempo real', () => {
    cy.visit('http://localhost:3000');
    cy.contains('Visão geral do sistema').should('be.visible');
    cy.contains('Conexões Ativas').should('exist');
  });
});
