describe('Match Cancellation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matchs')
  })

  it('should cancel a match', () => {
    // Create a match first to ensure we have one to cancel
    cy.contains('Ajouter un match').click()
    
    // Wait for modal
    cy.get('h2').contains('Ajouter un match').should('be.visible')
    
    const today = new Date().toISOString().split('T')[0]
    cy.get('input[type="date"]').eq(2).type(today) // The modal inputs are likely the last ones if others exist
    // Wait, there are filter inputs on the page too!
    // The modal is inside a div with z-50.
    // We should scope to the modal.
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="date"]').type(today)
        cy.get('input[type="time"]').type('10:00')
        cy.get('input[type="number"]').type('1')
        // Select teams (assuming we have some)
        cy.get('select').eq(0).find('option').eq(1).then(opt => cy.get('select').eq(0).select(opt.val()))
        cy.get('select').eq(1).find('option').eq(2).then(opt => cy.get('select').eq(1).select(opt.val()))
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Wait for modal to close
    cy.get('.fixed.z-50').should('not.exist')
    
    // Now find the match and cancel it
    // The cancel button is likely the "Modifier" button then changing status?
    // Or is there a delete button?
    // MatchesPage.vue has a delete button (trash icon) for "A_VENIR" matches.
    // But "Cancellation" usually means setting status to "ANNULE".
    // The test name says "cancel a match".
    // If we want to set status to ANNULE, we use Edit modal.
    
    // Let's try to Edit and set status to ANNULE
    cy.get('button[title="Modifier"]').first().click()
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('ANNULE') // Status select
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Verify status
    cy.contains('Annulé').should('be.visible')
  })
})
