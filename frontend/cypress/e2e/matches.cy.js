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
    cy.login('admin@padel.com', 'Admin@2025!')
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
    cy.get('input[placeholder="Entreprise"]').type('Team A')
    // Select players (assuming they are at the end of the list or searchable)
    // Since select options text contains firstname, we can select by text
    cy.get('select').eq(0).select(`${player1.firstname} ${player1.lastname} (${player1.company})`)
    cy.get('select').eq(1).select(`${player2.firstname} ${player2.lastname} (${player2.company})`)
    cy.contains('button', 'Créer').click()
    cy.contains('td', 'Team A').should('exist')

    // Team B
    cy.contains('button', 'Créer une équipe').click()
    cy.get('input[placeholder="Entreprise"]').type('Team B')
    cy.get('select').eq(0).select(`${player3.firstname} ${player3.lastname} (${player3.company})`)
    cy.get('select').eq(1).select(`${player4.firstname} ${player4.lastname} (${player4.company})`)
    cy.contains('button', 'Créer').click()
    cy.contains('td', 'Team B').should('exist')

    // 3. Create Match
    cy.visit('/matches')
    cy.contains('button', 'Ajouter un match').click()

    cy.get('input[type="date"]').type('2025-06-15')
    cy.get('input[type="time"]').type('14:00')
    cy.get('input[type="number"]').clear().type('1')

    // Select teams
    cy.get('select').eq(0).select('Team A')
    cy.get('select').eq(1).select('Team B')

    cy.contains('button', 'Enregistrer').click()

    // 4. Verify Match
    cy.contains('Dimanche 15 juin 2025').should('exist')
    cy.contains('Team A').should('exist')
    cy.contains('Team B').should('exist')
  })

  it('should filter matches', () => {
    cy.visit('/matches')
    // Assuming we have matches from previous test or seed
    cy.get('select').last().select('A_VENIR')
    cy.contains('Team A').should('exist')
  })
})
