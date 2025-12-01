describe('Results Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should allow admin to enter match results', () => {
    // Teams CompA and ResCompA are seeded
    
    // Create Match first
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()
    
    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-06-20')
      cy.get('input[type="time"]').type('10:00')
      cy.get('input[type="number"]').clear().type('2')
      cy.get('select').eq(0).select('CompA')
      cy.get('select').eq(1).select('ResCompA')
      cy.contains('button', 'Enregistrer').click()
    })

    // Le match est en 2026, les filtres par défaut s'arrêtent à J+30.
    // Il faut changer la date de fin pour voir le match qu'on vient de créer.
    cy.get('input[type="date"]').eq(1).type('2026-12-31') 

    // 2. Enter Results
    // Maintenant le match est visible, on peut le trouver
    cy.contains('CompA').parents('.border-l-4').within(() => {
      cy.get('button[title="Modifier"]').click()
    })

    // In Modal
    cy.get('div.fixed').contains('h2', 'Modifier le match').parents('div.fixed').within(() => {
      cy.get('select').last().select('Terminé')
      cy.get('input[placeholder="ex: 6-4 6-2"]').type('6-4, 6-4')
      cy.get('input[placeholder="ex: 4-6 2-6"]').type('4-6, 4-6')
      cy.contains('button', 'Enregistrer').click()
    })

    // 3. Verify Results
    cy.contains('CompA').parents('.border-l-4').within(() => {
      cy.contains('6-4, 6-4').should('exist')
      cy.contains('Terminé').should('exist')
    })
  })

  it('should display results in ranking', () => {
    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    cy.contains('td', 'CompA').should('exist')
    cy.contains('td', 'ResCompA').should('exist')
  })
})
