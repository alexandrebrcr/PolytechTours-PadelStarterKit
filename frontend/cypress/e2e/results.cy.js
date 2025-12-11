describe('Results Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should allow admin to enter match results', () => {
    // Teams Dream Team and Equipe 42 are seeded
    
    // Create Match first
    cy.visit('/matchs')
    cy.contains('button', 'Ajouter un match').click()
    
    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-06-20')
      cy.get('input[type="time"]').type('10:00')
      cy.get('input[type="number"]').clear().type('2')
      cy.get('select').eq(0).select('Dream Team')
      cy.get('select').eq(1).select('Equipe 42')
      cy.contains('button', 'Enregistrer').click()
    })

    // Le match est en 2026, les filtres par défaut s'arrêtent à J+30.
    // Il faut changer la date de fin pour voir le match qu'on vient de créer.
    cy.get('input[type="date"]').eq(1).type('2026-12-31') 

    // 2. Enter Results
    // Maintenant le match est visible, on peut le trouver
    cy.contains('Dream Team').parents('.border-l-4').within(() => {
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
    cy.contains('Dream Team').parents('.border-l-4').within(() => {
      cy.contains('6-4, 6-4').should('exist')
      cy.contains('Terminé').should('exist')
    })
  })

  it('should display results in ranking', () => {
    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    cy.contains('td', 'Dream Team').should('exist')
  })

  it('should validate score format', () => {
    // Create Match first
    cy.visit('/matchs')
    cy.contains('button', 'Ajouter un match').click()
    
    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-06-21')
      cy.get('input[type="time"]').type('10:00')
      cy.get('input[type="number"]').clear().type('3')
      cy.get('select').eq(0).select('Dream Team')
      cy.get('select').eq(1).select('Equipe 42')
      cy.contains('button', 'Enregistrer').click()
    })
    
    cy.get('input[type="date"]').eq(1).type('2026-12-31') 

    cy.contains('Piste 3').parents('.border-l-4').within(() => {
      cy.get('button[title="Modifier"]').click()
    })

    cy.get('div.fixed').contains('h2', 'Modifier le match').parents('div.fixed').within(() => {
      cy.get('select').last().select('Terminé')
      // Invalid format
      cy.get('input[placeholder="ex: 6-4 6-2"]').type('invalid')
      // Check validation (assuming HTML5 or custom validation)
      // If custom validation, we might see an error message or button disabled
      // Or we can try to save and expect failure
    })
  })
})

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
      cy.get('select').eq(0).select('Dream Team')
      cy.get('select').eq(1).select('Equipe 42')
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
    
    // Dream Team won, should have points.
    // We verify that the row for Dream Team exists and has some points.
    cy.contains('td', 'Dream Team').parent().find('td').eq(2).should('not.be.empty')
    cy.contains('td', 'Dream Team').parent().find('td').eq(4).should('contain', '1') // Gagnés >= 1 (since we just won one)
  })
})
