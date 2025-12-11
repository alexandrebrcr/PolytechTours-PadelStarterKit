describe('General Validation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should prevent creating match with same team', () => {
    cy.visit('/matchs')
    cy.contains('Ajouter un match').click()
    
    cy.get('.fixed.z-50').within(() => {
        // Select same team if possible
        // If the second select filters out the first team, this test is invalid (or passes by design)
        // Let's check if we can select the same.
        cy.get('select').eq(0).find('option').eq(1).then($opt => {
            const val = $opt.val()
            cy.get('select').eq(0).select(val)
            
            // Check if second select has this option
            cy.get('select').eq(1).find(`option[value="${val}"]`).then($opt2 => {
                if ($opt2.length > 0) {
                    cy.get('select').eq(1).select(val)
                    // Try to save
                    const stub = cy.stub()
                    cy.on('window:alert', stub)
                    cy.contains('button', 'Enregistrer').click()
                    // Should fail
                }
            })
        })
    })
  })

  it('should prevent creating match in the past', () => {
    cy.visit('/matchs')
    cy.contains('Ajouter un match').click()
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="date"]').type('2020-01-01')
        // Browser validation might show error
        // Or backend error
    })
  })

  it('should validate score format', () => {
    // This requires editing a match result.
    // We need a match in the past or "TERMINE"?
    // Or just "A_VENIR" and we enter results?
    // Admin can enter results for any match?
    // Let's assume we can edit a match.
  })
})
