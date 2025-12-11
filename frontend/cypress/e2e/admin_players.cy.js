describe('Admin Players Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/admin')
    // Wait for data to load
    cy.intercept('GET', '/api/v1/admin/players').as('getPlayers')
    cy.wait('@getPlayers')
    cy.contains('button', 'Joueurs').click()
  })

  it('should create a new player', () => {
    const timestamp = Date.now()
    const email = `newplayer${timestamp}@test.com`
    
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('New')
    cy.get('input[placeholder="Nom"]').type('Player')
    cy.get('input[placeholder="Entreprise"]').type('Test Corp')
    cy.get('input[type="email"]').type(email)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
    
    cy.intercept('POST', '/api/v1/admin/players').as('createPlayer')
    cy.contains('button', 'Enregistrer').click()
    cy.wait('@createPlayer').its('response.statusCode').should('eq', 200)
    
    // Verify modal closed
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')
    
    // Verify player in list (by name since email is not shown)
    cy.contains('New Player').should('be.visible')
  })

  it('should prevent creating player with existing email', () => {
      const timestamp = Date.now()
      const email = `dup${timestamp}@test.com`
      
      // Create first
      cy.contains('Ajouter un joueur').click()
      cy.get('input[placeholder="Prénom"]').type('First')
      cy.get('input[placeholder="Nom"]').type('User')
      cy.get('input[placeholder="Entreprise"]').type('Corp')
      cy.get('input[type="email"]').type(email)
      cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
      cy.contains('button', 'Enregistrer').click()
      
      // Wait for modal to close
      cy.contains('h3', 'Ajouter un joueur').should('not.exist')

      // Create duplicate
      cy.contains('Ajouter un joueur').click()
      cy.get('input[placeholder="Prénom"]').type('Second')
      cy.get('input[placeholder="Nom"]').type('User')
      cy.get('input[placeholder="Entreprise"]').type('Corp')
      cy.get('input[type="email"]').type(email)
      cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${(timestamp+1).toString().slice(-6)}`)
      
      // Stub alert
      const stub = cy.stub()
      cy.on('window:alert', stub)
      
      cy.contains('button', 'Enregistrer').click()
      
      cy.wrap(stub).should('be.called')
  })

  it('should validate license format', () => {
    cy.contains('Ajouter un joueur').click()
    
    // Invalid license
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type('12345')
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').should('match', ':invalid')
    
    // Valid license
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').clear().type('L123456')
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').should('not.match', ':invalid')
  })
})
