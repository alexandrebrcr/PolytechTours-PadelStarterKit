describe('Match Cancellation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matches') 
    // Verify we are logged in as admin
    cy.get('nav').contains('Administration').should('exist')
  })

  it('should cancel a match', () => {
    // Create a match first to ensure we have one to cancel
    cy.contains('button', 'Ajouter un match').click()
    
    // Wait for modal
    cy.contains('h2', 'Ajouter un match').should('be.visible')
    
    const today = new Date().toISOString().split('T')[0]
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="date"]').type(today)
        cy.get('input[type="time"]').type('10:00')
        cy.get('input[type="number"]').clear().type('1')
        // Select teams
        cy.get('select').eq(0).find('option').should('have.length.gt', 1)
        cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
        cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Wait for modal to close
    cy.get('.fixed.z-50').should('not.exist')
    
    // Modification du match
    cy.get('button[title="Modifier"]').first().click()
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('Annulé')
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Verify status
    cy.contains('Annulé').should('be.visible')
  })
})
