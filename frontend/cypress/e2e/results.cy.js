describe('Results Management', () => {
  const timestamp = Date.now()
  const player1 = {
    firstname: 'Alice',
    lastname: 'Test',
    company: 'ResCompA',
    email: `r1_${timestamp}@test.com`,
    license: `L${timestamp.toString().slice(-6)}`
  }
  const player2 = {
    firstname: 'Bob',
    lastname: 'Test',
    company: 'ResCompA',
    email: `r2_${timestamp}@test.com`,
    license: `L${(timestamp + 1).toString().slice(-6)}`
  }
  const player3 = {
    firstname: 'Charlie',
    lastname: 'Test',
    company: 'ResCompB',
    email: `r3_${timestamp}@test.com`,
    license: `L${(timestamp + 2).toString().slice(-6)}`
  }
  const player4 = {
    firstname: 'David',
    lastname: 'Test',
    company: 'ResCompB',
    email: `r4_${timestamp}@test.com`,
    license: `L${(timestamp + 3).toString().slice(-6)}`
  }

  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should allow admin to enter match results', () => {
    // 1. Setup: Create Players & Teams & Match
    // (Ideally this should be done via API to speed up tests, but UI is fine for E2E)
    cy.visit('/admin')

    const createPlayer = (p) => {
      cy.contains('button', 'Ajouter un joueur').click()
      cy.get('input[placeholder="Prénom"]').type(p.firstname)
      cy.get('input[placeholder="Nom"]').type(p.lastname)
      cy.get('input[placeholder="Entreprise"]').type(p.company)
      cy.get('input[type="email"]').type(p.email)
      cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(p.license)
      cy.contains('button', 'Enregistrer').click()
      cy.contains('tr', p.firstname).should('exist')
    }

    createPlayer(player1)
    createPlayer(player2)
    createPlayer(player3)
    createPlayer(player4)

    cy.contains('button', 'Équipes').click()

    // Team A
    cy.contains('button', 'Créer une équipe').click()
    cy.get('input[placeholder="Entreprise"]').type('ResCompA')
    
    cy.get('select').eq(0).find('option').contains(player1.firstname).then($opt => {
      cy.get('select').eq(0).select($opt.text())
    })
    cy.get('select').eq(1).find('option').contains(player2.firstname).then($opt => {
      cy.get('select').eq(1).select($opt.text())
    })
    
    cy.contains('button', 'Créer').click({ force: true })

    // Team B
    cy.contains('button', 'Créer une équipe').click()
    cy.get('input[placeholder="Entreprise"]').type('ResCompB')
    
    cy.get('select').eq(0).find('option').contains(player3.firstname).then($opt => {
      cy.get('select').eq(0).select($opt.text())
    })
    cy.get('select').eq(1).find('option').contains(player4.firstname).then($opt => {
      cy.get('select').eq(1).select($opt.text())
    })
    
    cy.contains('button', 'Créer').click({ force: true })

    // Create Match
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()
    cy.get('input[type="date"]').type('2025-06-20')
    cy.get('input[type="time"]').type('10:00')
    cy.get('input[type="number"]').clear().type('2')
    cy.get('select').eq(0).select('ResCompA')
    cy.get('select').eq(1).select('ResCompB')
    cy.contains('button', 'Enregistrer').click()

    // 2. Enter Results
    // Find the match card (assuming it's the one we just created, or filter by team)
    cy.contains('ResCompA').parents('.border-l-4').within(() => {
      cy.get('button[title="Modifier"]').click()
    })

    // In Modal
    cy.get('select').last().select('Terminé') // Status
    cy.get('input[placeholder="ex: 6-4 6-2"]').first().type('6-4 6-4')
    cy.get('input[placeholder="ex: 4-6 2-6"]').last().type('4-6 4-6') // Just dummy values
    cy.contains('button', 'Enregistrer').click()

    // 3. Verify Results
    cy.contains('ResCompA').parents('.border-l-4').within(() => {
      cy.contains('6-4 6-4').should('exist')
      cy.contains('Terminé').should('exist')
    })
  })

  it('should display results in ranking', () => {
    cy.visit('/results')
    cy.contains('button', 'Classement Général').click()
    // Check if our teams appear (might need reload or wait if async)
    // Note: Ranking calculation might depend on backend logic. 
    // If we just entered a result, it should appear.
    cy.contains('td', 'ResCompA').should('exist')
    cy.contains('td', 'ResCompB').should('exist')
  })
})
