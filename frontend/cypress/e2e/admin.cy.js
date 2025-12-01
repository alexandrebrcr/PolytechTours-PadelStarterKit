describe('Administration', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('http://localhost:5173')
  })

  it('Auto-rétrogradation redirige vers l\'accueil', () => {
    const timestamp = Date.now()
    const email = `admin${timestamp}@test.com`
    const license = `L${timestamp.toString().slice(-6)}`
    // Use letters only for names because of regex validation
    const randomLetters = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5) || 'abcde'
    const firstname = `Admin${randomLetters}`
    const lastname = `Test${randomLetters}`

    // 1. Connexion Admin Suprême
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Test@2025_2026')
    cy.get('button[type="submit"]').click()

    // 2. Créer un nouveau joueur qui sera admin
    cy.contains('Administration').click()
    cy.contains('Joueurs').click()
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type(firstname)
    cy.get('input[placeholder="Nom"]').type(lastname)
    cy.get('input[placeholder="Entreprise"]').type('Test Corp')
    cy.get('input[type="email"]').type(email)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(license)
    cy.contains('button', 'Enregistrer').click()

    // 3. Créer son compte
    // On cherche la ligne avec le nom unique
    cy.contains('tr', firstname).contains('Créer compte').click()
    cy.get('.bg-yellow-100').invoke('text').then((tempPassword) => {
      cy.contains('Fermer').click()

      // 4. Le promouvoir Admin
      cy.contains('tr', firstname).contains('Promouvoir Admin').click()

      // 5. Se déconnecter
      cy.contains('Déconnexion').click()

      // 6. Se connecter avec le nouvel admin
      cy.get('input[type="email"]').type(email)
      cy.get('input[type="password"]').type(tempPassword)
      cy.get('button[type="submit"]').click()

      // Changer le mot de passe (obligatoire)
      cy.contains('Changement de mot de passe requis').should('be.visible')
      const newPass = 'AdminPass123!'
      cy.get('input[type="password"]').eq(1).type(newPass)
      cy.get('input[type="password"]').eq(2).type(newPass)
      cy.contains('button', 'Changer le mot de passe').click()

      // 7. Aller sur la page admin
      cy.contains('Administration').click()

      // 8. Se rétrograder
      // On doit trouver la ligne correspondant à notre utilisateur
      cy.contains('tr', firstname).within(() => {
        cy.contains('Rétrograder').click()
      })

      // 9. Vérifier la redirection et l'absence du menu Admin
      cy.url().should('eq', 'http://localhost:5173/')
      cy.contains('Administration').should('not.exist')

      // 10. Vérifier qu'on ne peut plus accéder à /admin
      cy.visit('/admin')
      cy.url().should('eq', 'http://localhost:5173/')
    })
  })
})
