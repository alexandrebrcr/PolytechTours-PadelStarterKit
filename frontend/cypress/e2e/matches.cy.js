describe('Matches Management', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'AdminP@ssw0rd123')
  })

  it('should display matches page', () => {
    cy.visit('/matches')
    cy.contains('h1', 'Matchs')
  })

  it('should allow admin to create a match', () => {
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()
    
    cy.get('input[type="date"]').type('2025-01-15')
    cy.get('input[type="time"]').type('19:30')
    cy.get('input[type="number"]').clear().type('1')
    
    // Assuming teams are loaded
    cy.get('select').eq(0).select(1) // Select first team
    cy.get('select').eq(1).select(2) // Select second team
    
    cy.contains('button', 'Enregistrer').click()
    
    // Should close modal and refresh list
    cy.contains('Lundi 15 janvier 2025')
  })

  it('should filter matches', () => {
    cy.visit('/matches')
    cy.get('select').last().select('A_VENIR')
    // Check if filtered
  })
})
