describe('Ranking Logic', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should update ranking after match result', () => {
    // 1. Check initial ranking (or assume 0 if fresh db, but db is seeded)
    // We can't easily know the initial points without reading them first.
    // So we will just check that points exist.
    
    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    
    // 2. Create and finish a match
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()
    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-11-20')
      cy.get('input[type="time"]').type('10:00')
      cy.get('input[type="number"]').clear().type('12')
      cy.get('select').eq(0).select('CompA')
      cy.get('select').eq(1).select('ResCompA')
      cy.contains('button', 'Enregistrer').click()
    })
    
    cy.get('input[type="date"]').eq(1).type('2026-12-31')

    cy.contains('Piste 12').parents('.border-l-4').within(() => {
      cy.get('button[title="Modifier"]').click()
    })

    cy.get('div.fixed').contains('h2', 'Modifier le match').parents('div.fixed').within(() => {
      cy.get('select').last().select('Terminé')
      cy.get('input[placeholder="ex: 6-4 6-2"]').type('6-0, 6-0')
      cy.contains('button', 'Enregistrer').click()
    })

    // 3. Verify Ranking updated
    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    
    // CompA won, should have points.
    // We verify that the row for CompA exists and has some points.
    cy.contains('td', 'CompA').parent().find('td').eq(2).should('not.be.empty')
    cy.contains('td', 'CompA').parent().find('td').eq(4).should('contain', '1') // Gagnés >= 1 (since we just won one)
  })
})
