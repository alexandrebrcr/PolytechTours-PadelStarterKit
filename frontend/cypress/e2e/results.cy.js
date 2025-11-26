describe('Results & Ranking', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'ValidP@ssw0rd123')
  })

  it('should display results page with tabs', () => {
    cy.visit('/results')
    cy.contains('h1', 'Résultats & Classement')
    cy.contains('button', 'Mes Résultats')
    cy.contains('button', 'Classement Général')
  })

  it('should display ranking table', () => {
    // Mock ranking data
    cy.intercept('GET', '/api/v1/results/ranking', {
      statusCode: 200,
      body: [
        {
          position: 1,
          company: 'Company A',
          matches_played: 10,
          wins: 8,
          losses: 2,
          points: 24,
          sets_won: 18,
          sets_lost: 6
        },
        {
          position: 2,
          company: 'Company B',
          matches_played: 10,
          wins: 6,
          losses: 4,
          points: 18,
          sets_won: 14,
          sets_lost: 10
        }
      ]
    }).as('getRanking')

    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    cy.wait('@getRanking')

    cy.get('table').should('exist')
    cy.contains('td', 'Company A')
    cy.contains('td', '24') // Points
    cy.contains('td', 'Company B')
    cy.contains('td', '18')
  })

  it('should display history', () => {
    // Mock matches history
    cy.intercept('GET', '/api/v1/matches*', {
      statusCode: 200,
      body: [
        {
          id: 1,
          date: '2025-01-10',
          time: '19:00:00',
          court_number: 1,
          status: 'TERMINE',
          score_team1: '6-4, 6-3',
          team1: { id: 1, company: 'My Company', players: [] },
          team2: { id: 2, company: 'Opponent Corp', players: [] }
        }
      ]
    }).as('getHistory')

    cy.visit('/results')
    // Default tab is history
    cy.wait('@getHistory')
    
    cy.contains('My Company')
    cy.contains('Opponent Corp')
    cy.contains('6-4, 6-3')
  })
})
