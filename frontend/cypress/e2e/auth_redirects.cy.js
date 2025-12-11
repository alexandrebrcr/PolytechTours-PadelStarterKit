describe('Auth Redirects', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should logout from profile page', () => {
    cy.visit('/profile')
    cy.contains('Déconnexion').click()
    cy.url().should('include', '/login')
  })

  it('should logout from admin page', () => {
    cy.visit('/admin')
    cy.contains('Déconnexion').click()
    cy.url().should('include', '/login')
  })

  it('should redirect to home if logged in and visiting login', () => {
    cy.visit('/login')
    cy.url().should('eq', 'http://localhost:5173/')
  })
})
