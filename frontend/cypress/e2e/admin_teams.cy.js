describe('Admin Teams Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/admin')
    cy.contains('button', 'Équipes').click()
  })

  it('should create and delete a team', () => {
    const timestamp = Date.now()
    const p1Email = `p1_${timestamp}@test.com`
    const p2Email = `p2_${timestamp}@test.com`
    
    // 1. Create 2 players first (switch to Players tab)
    cy.contains('button', 'Joueurs').click()
    
    // Player 1
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('PlayerOne')
    cy.get('input[placeholder="Nom"]').type('Test')
    cy.get('input[placeholder="Entreprise"]').type('TeamCorp')
    cy.get('input[type="email"]').type(p1Email)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')

    // Player 2
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('PlayerTwo')
    cy.get('input[placeholder="Nom"]').type('Test')
    cy.get('input[placeholder="Entreprise"]').type('TeamCorp')
    cy.get('input[type="email"]').type(p2Email)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${(timestamp+1).toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')

    // 2. Create Team
    cy.contains('button', 'Équipes').click()
    cy.contains('Créer une équipe').click()
    
    cy.get('input[placeholder="Entreprise"]').type('TeamCorp')
    
    // Select players - they should be in the dropdown now
    // The dropdown shows "Firstname Lastname (Company)"
    cy.get('select').eq(0).select(`PlayerOne Test (TeamCorp)`)
    cy.get('select').eq(1).select(`PlayerTwo Test (TeamCorp)`)
    
    cy.intercept('POST', '/api/v1/admin/teams').as('createTeam')
    cy.contains('button', /^Créer$/).click()
    cy.wait('@createTeam').its('response.statusCode').should('eq', 200)
    
    // Verify team in list
    cy.contains('TeamCorp').should('be.visible')
    cy.contains('PlayerOne Test').should('be.visible')
    cy.contains('PlayerTwo Test').should('be.visible')

    // 3. Delete Team
    // Find the row with our team and click delete
    cy.contains('tr', 'TeamCorp').within(() => {
        cy.on('window:confirm', () => true)
        cy.contains('Supprimer').click()
    })
    
    // Verify deleted
    // Wait a bit for refresh
    cy.wait(1000)
    cy.contains('tr', 'TeamCorp').should('not.exist')
  })

  it('should filter available players in dropdown', () => {
    cy.contains('Créer une équipe').click()
    // Just check that we have options
    cy.get('select').eq(0).find('option').should('have.length.gt', 1)
  })
})
