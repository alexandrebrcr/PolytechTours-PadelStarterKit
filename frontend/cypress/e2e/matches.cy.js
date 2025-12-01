describe('Matches Management', () => {
  const timestamp = Date.now()
  // Use letters only for names to pass backend validation
  const player1 = {
    firstname: 'Pierre',
    lastname: 'Test',
    company: 'CompA',
    email: `p1_${timestamp}@test.com`,
    license: `L${timestamp.toString().slice(-6)}`
  }
  const player2 = {
    firstname: 'Paul',
    lastname: 'Test',
    company: 'CompA',
    email: `p2_${timestamp}@test.com`,
    license: `L${(timestamp + 1).toString().slice(-6)}`
  }
  const player3 = {
    firstname: 'Jacques',
    lastname: 'Test',
    company: 'CompB',
    email: `p3_${timestamp}@test.com`,
    license: `L${(timestamp + 2).toString().slice(-6)}`
  }
  const player4 = {
    firstname: 'Jean',
    lastname: 'Test',
    company: 'CompB',
    email: `p4_${timestamp}@test.com`,
    license: `L${(timestamp + 3).toString().slice(-6)}`
  }

  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
  })

  it('should allow admin to create teams and a match', () => {
    // 1. Create Players
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

    // 2. Create Teams
    cy.contains('button', 'Équipes').click()

    // Team A
    cy.contains('button', 'Créer une équipe').click()
    cy.get('input[placeholder="Entreprise"]').type('CompA')

    // Select players robustly
    cy.get('select').eq(0).find('option').contains(player1.firstname).then($opt => {
      cy.get('select').eq(0).select($opt.text())
    })
    cy.get('select').eq(1).find('option').contains(player2.firstname).then($opt => {
      cy.get('select').eq(1).select($opt.text())
    })

    cy.contains('button', 'Créer').click({ force: true })
    cy.contains('td', 'CompA').should('exist')

    // Team B
    cy.contains('button', 'Créer une équipe').click()
    cy.get('input[placeholder="Entreprise"]').type('CompB')

    cy.get('select').eq(0).find('option').contains(player3.firstname).then($opt => {
      cy.get('select').eq(0).select($opt.text())
    })
    cy.get('select').eq(1).find('option').contains(player4.firstname).then($opt => {
      cy.get('select').eq(1).select($opt.text())
    })

    cy.contains('button', 'Créer').click({ force: true })
    cy.contains('td', 'CompB').should('exist')

    // 3. Create Match
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()

    cy.get('input[type="date"]').type('2025-06-15')
    cy.get('input[type="time"]').type('14:00')
    cy.get('input[type="number"]').clear().type('1')

    // Select teams
    cy.get('select').eq(0).select('CompA')
    cy.get('select').eq(1).select('CompB')

    cy.contains('button', 'Enregistrer').click()

    // 4. Verify Match
    cy.contains('Dimanche 15 juin 2025').should('exist')
    cy.contains('CompA').should('exist')
    cy.contains('CompB').should('exist')
  })

  it('should filter matches', () => {
    cy.visit('/matches')
    // Assuming we have matches from previous test or seed
    cy.get('select').last().select('A_VENIR')
    cy.contains('CompA').should('exist')
  })
})
