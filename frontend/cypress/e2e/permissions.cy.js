describe('User Permissions', () => {
  const timestamp = Date.now()
  const userEmail = `user${timestamp}@test.com`
  const userPass = 'UserPass123!'
  
  before(() => {
    // Create a regular user via Admin first
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/admin')
    
    // Create player
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('Regular')
    cy.get('input[placeholder="Nom"]').type(`User${timestamp}`)
    cy.get('input[placeholder="Entreprise"]').type('Test Corp')
    cy.get('input[type="email"]').type(userEmail)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()

    // Create account
    cy.contains('tr', userEmail).contains('Créer compte').click()
    cy.get('.bg-yellow-100').invoke('text').as('tempPassword')
    cy.contains('Fermer').click()
    cy.contains('Déconnexion').click()
  })

  it('should setup regular user password', function() {
    // First login with temp password
    cy.visit('/login')
    cy.get('input[type="email"]').type(userEmail)
    cy.get('input[type="password"]').type(this.tempPassword)
    cy.get('button[type="submit"]').click()

    // Change password
    cy.contains('Changement de mot de passe requis').should('be.visible')
    cy.get('input[type="password"]').eq(1).type(userPass)
    cy.get('input[type="password"]').eq(2).type(userPass)
    cy.contains('button', 'Changer le mot de passe').click()
    
    cy.url().should('eq', 'http://localhost:5173/')
  })

  context('As Regular User', () => {
    beforeEach(() => {
      cy.login(userEmail, userPass)
    })

    it('should not see Administration link', () => {
      cy.contains('Administration').should('not.exist')
    })

    it('should be redirected from /admin', () => {
      cy.visit('/admin')
      cy.url().should('eq', 'http://localhost:5173/')
    })

    it('should not see "Ajouter un match" button', () => {
      cy.visit('/matches')
      cy.contains('button', 'Ajouter un match').should('not.exist')
    })

    it('should not see edit/delete buttons on matches', () => {
      cy.visit('/matches')
      // Assuming there are matches
      cy.get('.border-l-4').each(($el) => {
        cy.wrap($el).find('button[title="Modifier"]').should('not.exist')
        cy.wrap($el).find('button[title="Supprimer"]').should('not.exist')
      })
    })

    it('should not see "Ajouter un événement" in planning', () => {
      cy.visit('/planning')
      cy.contains('button', 'Ajouter un événement').should('not.exist')
    })
  })
})
