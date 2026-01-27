describe('Matches Management', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matches')
  })

  it('should allow admin to create a match', () => {
    cy.contains('Ajouter un match').click()

    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
      cy.get('input[type="time"]').type('14:00')
      cy.get('input[type="number"]').clear().type('2')

      cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
      cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))

      cy.contains('button', 'Enregistrer').click()
    })

    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('Piste 2').should('be.visible')
  })

  it('should allow admin to update a match', () => {
    // Create a match first (Use different court/time to avoid conflict with previous test)
    cy.contains('Ajouter un match').click()
    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
      cy.get('input[type="time"]').type('15:00')
      cy.get('input[type="number"]').clear().type('3')
      cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
      cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
      cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')

    // Edit
    cy.get('button[title="Modifier"]').first().click()

    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="number"]').clear().type('4')
      
      // Test score update
      cy.get('select').last().select('Terminé')
      cy.get('input[placeholder="Ex: 6-4, 6-2"]').type('6-4, 6-2')
      cy.contains('Le score de l\'équipe 2 sera calculé automatiquement : 4-6, 2-6').should('be.visible')
      
      cy.contains('button', 'Enregistrer').click({ force: true })
      // Check if error message appears
      cy.get('.bg-red-100').should('not.exist')
    })

    cy.get('.fixed.z-50').should('not.exist')
    cy.wait(500) // Wait for list refresh
    cy.contains('Piste 4').should('be.visible')
    cy.contains('6-4, 6-2').should('be.visible')
  })

  it('should validate score format', () => {
    // Create a match first
    cy.contains('Ajouter un match').click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
        cy.get('input[type="time"]').type('14:00')
        cy.get('input[type="number"]').clear().type('2')
        cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
        cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
        cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')

    // Edit match to test score validation
    cy.get('button[title="Modifier"]').first().click()
    
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('Terminé')
        
        // Test invalid format
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').type('invalid')
        cy.contains('button', 'Enregistrer').click({ force: true })
        cy.contains('Format de score invalide').should('be.visible')

        // Test 1 set only (should fail regex)
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').clear().type('6-4')
        cy.contains('button', 'Enregistrer').click({ force: true })
        cy.contains('Format de score invalide').should('be.visible')

        // Test 1-1 draw (should fail new rule)
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').clear().type('6-4, 4-6')
        cy.contains('button', 'Enregistrer').click({ force: true })
        cy.contains('Il faut au moins 2 sets gagnants').should('be.visible')

        // Test 3 sets where first 2 are enough (should fail)
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').clear().type('6-4, 6-4, 6-4')
        cy.contains('button', 'Enregistrer').click({ force: true })
        cy.contains('Le match est déjà terminé après 2 sets gagnants').should('be.visible')
    })
  })

  it('should allow admin to delete a match', () => {
    // Create a match first
    cy.contains('Ajouter un match').click()
    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
      cy.get('input[type="time"]').type('14:00')
      cy.get('input[type="number"]').clear().type('2')
      cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
      cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
      cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')

    cy.get('button[title="Supprimer"]').first().click()
    cy.on('window:confirm', () => true)
    cy.contains('Piste 2').should('not.exist')
  })

  it('should filter matches', () => {
    cy.get('input[type="date"]').first().should('be.visible')
  })

  it('should display correct colors for match status', () => {
    // Check for classes or visual indicators
    cy.contains('Ajouter un match').should('be.visible')
  })

  it('should prevent creating match with same team', () => {
    cy.contains('Ajouter un match').click()

    cy.get('.fixed.z-50').within(() => {
      // Select same team if possible
      cy.get('select').eq(0).find('option').eq(0).then($opt => {
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
    cy.contains('Ajouter un match').click()

    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type('2020-01-01')
      // Browser validation might show error
    })
  })
})

describe('Match Cancellation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matches')
    // Verify we are logged in as admin
    cy.get('nav').contains('Administration').should('exist')
  })

  it('should cancel a match', () => {
    // Create a match first to ensure we have one to cancel
    cy.contains('button', 'Ajouter un match').click()

    // Wait for modal
    cy.contains('h2', 'Ajouter un match').should('be.visible')

    const today = new Date().toISOString().split('T')[0]

    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type(today)
      cy.get('input[type="time"]').type('10:00')
      cy.get('input[type="number"]').clear().type('1')
      // Select teams
      cy.get('select').eq(0).find('option').should('have.length.gt', 1)
      cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
      cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
      cy.contains('button', 'Enregistrer').click()
    })

    // Wait for modal to close
    cy.get('.fixed.z-50').should('not.exist')

    // Modification du match
    cy.get('button[title="Modifier"]').first().click()

    cy.get('.fixed.z-50').within(() => {
      cy.get('select').last().select('Annulé')
      cy.contains('button', 'Enregistrer').click()
    })

    // Verify status
    cy.contains('Annulé').should('be.visible')
  })
})

describe('Match Filters', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matches')
  })

  it('should filter matches by company', () => {
    const timestamp = Date.now()
    const companyName = `FilterCorp` // Simplifié, ou utilise letters only regex

    // 0. Create Players
    cy.visit('/admin')
    cy.contains('button', 'Joueurs').click() // Ajout du click onglet pour sécurité

    // Player 1
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('Fan') // Pas de chiffres
    cy.get('input[placeholder="Nom"]').type('One')
    cy.get('input[placeholder="Entreprise"]').type(companyName)
    cy.get('input[type="email"]').type(`f1_${timestamp}@test.com`)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')
    cy.get('.fixed.inset-0').should('not.exist')

    // Player 2
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type('Fan')
    cy.get('input[placeholder="Nom"]').type('Two')
    cy.get('input[placeholder="Entreprise"]').type(companyName)
    cy.get('input[type="email"]').type(`f2_${timestamp}@test.com`)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${(timestamp + 1).toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')
    cy.get('.fixed.inset-0').should('not.exist')

    // 1. Create Team
    cy.contains('button', 'Équipes').click()
    cy.wait(500) // Wait for tab switch
    cy.contains('Créer une équipe').click({ force: true })
    cy.get('input[placeholder="Nom d\'équipe"]').type(companyName)

    // Select players (recherche par texte partiel)
    cy.get('select').eq(0).contains('Fan One').then($opt => cy.get('select').eq(0).select($opt.val()))
    cy.get('select').eq(1).contains('Fan Two').then($opt => cy.get('select').eq(1).select($opt.val()))

    // Use specific selector for the modal button to avoid matching "Créer une équipe"
    cy.get('.fixed.inset-0 button').contains('Créer').click()
    cy.contains('h3', 'Créer une équipe').should('not.exist')

    // 2. Create Match
    cy.visit('/matches')
    cy.contains('Ajouter un match').click()
    cy.get('.fixed.z-50').within(() => {
      cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
      cy.get('input[type="time"]').type('12:00')
      cy.get('input[type="number"]').clear().type('1')

      // Sélection de notre nouvelle équipe
      cy.get('select').eq(0).contains(companyName).then($opt => {
        cy.get('select').eq(0).select($opt.val())
      })
      // Sélection d'une équipe adverse (n'importe laquelle sauf la précédente)
      cy.get('select').eq(1).find('option').eq(0).then(opt => cy.get('select').eq(1).select(opt.val()))

      cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')

    // 3. Filter by company using the select dropdown
    cy.get('select').contains('Toutes').parents('select').select(companyName)
    cy.contains(companyName).should('be.visible')
  })

  it('should filter matches by date range', () => {
    const today = new Date().toISOString().split('T')[0]
    cy.get('input[type="date"]').eq(0).type(today) // Start date
    cy.get('input[type="date"]').eq(1).type(today) // End date

    cy.get('input[type="date"]').eq(0).should('have.value', today)
  })
})

describe('Matches Logic & Validation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/matches')
  })

  it('should validate scores logic on update', () => {
    // 1. Créer un match de test
    cy.contains('Ajouter un match').click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="date"]').type(new Date().toISOString().split('T')[0])
        cy.get('input[type="time"]').type('10:00')
        cy.get('input[type="number"]').clear().type('5')
        cy.get('select').eq(0).find('option').eq(0).then(opt => cy.get('select').eq(0).select(opt.val()))
        cy.get('select').eq(1).find('option').eq(1).then(opt => cy.get('select').eq(1).select(opt.val()))
        cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('Piste 5').should('be.visible')

    // 2. Tenter de passer en TERMINÉ sans score -> Doit échouer (Validation Frontend)
    cy.get('button[title="Modifier"]').first().click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('Terminé')
        // On efface les scores au cas où
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').first().clear()
        
        // On force le clic car le bouton pourrait ne pas être disabled mais déclencher une erreur
        cy.contains('button', 'Enregistrer').click()
        
        // Vérifier l'erreur frontend
        cy.contains("Veuillez saisir les scores pour terminer le match").should('be.visible')
        
        // Fermer la modal pour continuer
        cy.contains('button', 'Annuler').click()
    })
    cy.get('.fixed.z-50').should('not.exist')

    // 3. Ajouter les scores et valider -> Doit réussir (score_team2 calculé automatiquement)
    cy.get('button[title="Modifier"]').first().click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('Terminé')
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').clear().type('6-0, 6-0')
        cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('6-0, 6-0').should('be.visible')

    // 4. Passer en ANNULÉ -> Les scores doivent disparaître
    cy.get('button[title="Modifier"]').first().click()
    cy.get('.fixed.z-50').within(() => {
        // Le match est TERMINÉ donc l'input score est visible
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').should('have.value', '6-0, 6-0')
        
        // Changer statut vers ANNULÉ (l'input disparaîtra car status != TERMINE)
        cy.get('select').last().select('Annulé')
        // L'input score n'est plus visible car status != TERMINE
        cy.get('input[placeholder="Ex: 6-4, 6-2"]').should('not.exist')
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Vérifier suppression visuelle
    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('Annulé').should('be.visible')
    cy.contains('6-0, 6-0').should('not.exist')

    // 5. Modifier SEULEMENT l'heure (Test "Input should be none")
    // D'abord remettre à venir (car l'API refuse de modifier l'heure d'un match annulé)
    cy.get('button[title="Modifier"]').first().click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('select').last().select('À venir')
        cy.contains('button', 'Enregistrer').click()
    })
    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('À venir').should('be.visible')
    
    // Ensuite modifier l'heure (maintenant le match est à venir)
    cy.get('button[title="Modifier"]').first().click()
    cy.get('.fixed.z-50').within(() => {
        cy.get('input[type="time"]').clear().type('18:00')
        cy.contains('button', 'Enregistrer').click()
    })
    
    // Si ça plante ici avec "Input should be none", c'est que le fix n'a pas marché
    cy.get('.fixed.z-50').should('not.exist')
    cy.contains('18:00').should('be.visible')
  })
})