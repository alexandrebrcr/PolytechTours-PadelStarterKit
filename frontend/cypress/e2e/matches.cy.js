describe('Matches Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should allow admin to create a match', () => {
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()

    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-06-15')
      cy.get('input[type="time"]').type('14:00')
      cy.get('input[type="number"]').clear().type('1')

      cy.get('select').eq(0).select('CompA')
      cy.get('select').eq(1).select('ResCompA')

      cy.contains('button', 'Enregistrer').click()
    })

    // Le modal doit se fermer
    cy.get('div.fixed').should('not.exist')

    // Élargir le filtre de date pour voir 2026
    cy.get('input[type="date"]').eq(1).type('2026-12-31')

    // Utilisation de /.../i pour ignorer la majuscule/minuscule
    cy.contains(/lundi 15 juin 2026/i).should('exist') 
    cy.contains('CompA').should('exist')
    cy.contains('ResCompA').should('exist')
  })

  it('should filter matches', () => {
    cy.visit('/matches')
    
    // 1. Création du match
    cy.contains('button', 'Ajouter un match').click()
    cy.get('div.fixed').contains('h2', 'Ajouter un match').parents('div.fixed').within(() => {
      cy.get('input[type="date"]').type('2026-06-15')
      cy.get('input[type="time"]').type('14:00')
      cy.get('input[type="number"]').clear().type('1')
      cy.get('select').eq(0).select('CompA')
      cy.get('select').eq(1).select('ResCompA')
      cy.contains('button', 'Enregistrer').click()
    })

    // 2. Il faut AUSSI élargir la date ici pour que le match apparaisse
    cy.get('input[type="date"]').eq(1).type('2026-12-31')

    // 3. Test du filtre Statut
    cy.contains('label', 'Statut').next('select').select('À venir') 
    
    // Vérification
    cy.contains('CompA').should('exist')
  })
})
