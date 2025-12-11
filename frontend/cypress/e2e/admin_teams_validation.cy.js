describe('Admin Teams Validation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/admin')
    cy.contains('button', 'Équipes').click()
  })

  it('should prevent creating team with same player twice', () => {
    // Ensure modal is closed first
    cy.get('body').then($body => {
        if ($body.find('.fixed.inset-0').length > 0) {
            cy.contains('Annuler').click({force: true})
        }
    })

    cy.contains('Créer une équipe').click()
    
    // Wait for modal
    cy.get('h3').contains('Créer une équipe').should('be.visible')
    
    // Select same player in both dropdowns
    // We need at least one player available
    cy.get('select').eq(0).find('option').eq(1).then($opt => {
        const val = $opt.val()
        if (val) {
            cy.get('select').eq(0).select(val)
            cy.get('select').eq(1).select(val)
            
            // Browser validation might prevent submission or backend error
            // The HTML5 validation won't catch this (different selects)
            // So we expect backend error or frontend check
            
            // Stub alert
            const stub = cy.stub()
            cy.on('window:alert', stub)
            
            cy.contains('button', 'Créer').click()
            
            // Expect alert
            cy.wrap(stub).should('be.called')
        } else {
            cy.log('No players available to test')
        }
    })
  })
})
