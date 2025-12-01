describe('Gestion du Profil', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    // Se connecter avant chaque test
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Test@2025_2026')
    cy.get('button[type="submit"]').click()
    cy.url().should('eq', 'http://localhost:5173/')

    // Aller sur la page de profil
    cy.visit('/profile')
  })

  it('Affiche les informations du profil', () => {
    cy.contains('Informations personnelles').should('be.visible')
    cy.get('input[type="email"]').should('have.value', 'admin@padel.com')
    // Le numéro de licence doit être désactivé
    cy.contains('N° de licence').next('input').should('be.disabled')
  })

  it('Permet de modifier les informations personnelles', () => {
    // Remplir le formulaire
    cy.contains('Prénom').next('input').clear().type('Jean')
    cy.contains('Nom').next('input').clear().type('Dupont')
    cy.contains('Date de naissance').next('input').type('1990-01-01')

    // Sauvegarder
    cy.contains('Enregistrer').click()

    // Vérifier le message de succès
    cy.contains('Profil mis à jour avec succès').should('be.visible')

    // Recharger la page pour vérifier la persistance
    cy.reload()
    cy.contains('Prénom').next('input').should('have.value', 'Jean')
    cy.contains('Nom').next('input').should('have.value', 'Dupont')
  })

  it('Valide les champs du formulaire de profil', () => {
    // Nom invalide (chiffres)
    cy.contains('Prénom').next('input').clear().type('Jean123')
    // Remplir la date pour passer la validation HTML5
    cy.contains('Date de naissance').next('input').type('1990-01-01')
    cy.contains('Enregistrer').click()

    // Le backend doit renvoyer une erreur car le nom contient des chiffres
    // Le composant ProfilePage affiche l'erreur dans une notification
    cy.contains('Le nom/prénom ne doit contenir que des lettres, espaces, tirets et apostrophes').should('be.visible')
  })

  it('Permet de changer le mot de passe', () => {
    // Changer d'onglet
    cy.contains('Sécurité').click()

    // Remplir le formulaire
    cy.contains('Mot de passe actuel').next('input').type('Test@2025_2026')
    cy.contains('Nouveau mot de passe').next('input').type('NewPass123!@#')
    cy.contains('Confirmer le mot de passe').next('input').type('NewPass123!@#')

    cy.contains('Modifier le mot de passe').click()

    // Vérifier le succès
    cy.contains('Mot de passe modifié avec succès').should('be.visible')

    // Vérifier qu'on peut se connecter avec le nouveau mot de passe
    cy.contains('Déconnexion').click()
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('NewPass123!@#')
    cy.get('button[type="submit"]').click()
    cy.url().should('eq', 'http://localhost:5173/')

    // Remettre l'ancien mot de passe pour ne pas casser les autres tests
    cy.visit('/profile')
    cy.contains('Sécurité').click()
    cy.contains('Mot de passe actuel').next('input').type('NewPass123!@#')
    cy.contains('Nouveau mot de passe').next('input').type('Test@2025_2026')
    cy.contains('Confirmer le mot de passe').next('input').type('Test@2025_2026')
    cy.contains('Modifier le mot de passe').click()
  })

  it('Vérifie la correspondance des mots de passe', () => {
    cy.contains('Sécurité').click()

    cy.contains('Mot de passe actuel').next('input').type('Test@2025_2026')
    cy.contains('Nouveau mot de passe').next('input').type('NewPass123!@#')
    cy.contains('Confirmer le mot de passe').next('input').type('DifferentPass123!')

    cy.contains('Modifier le mot de passe').click()

    cy.contains('Les mots de passe ne correspondent pas').should('be.visible')
  })

  it('Gère l\'upload de photo de profil', () => {
    // On ne peut pas facilement tester le file upload réel sans fixture, 
    // mais on peut vérifier que le bouton existe et déclenche l'input
    cy.get('input[type="file"]').should('exist')

    // Simulation d'upload (nécessite un fichier dans cypress/fixtures)
    // cy.get('input[type="file"]').selectFile('cypress/fixtures/profile.jpg', { force: true })
    // cy.contains('Photo de profil mise à jour').should('be.visible')
  })
})
