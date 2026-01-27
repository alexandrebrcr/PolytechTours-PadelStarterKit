describe('Gestion du Profil', () => {
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Test@2025_2026')
    cy.get('button[type="submit"]').click()
    cy.url().should('eq', 'http://localhost:5173/')

    cy.visit('/profile')
  })

  it('Affiche les informations du profil', () => {
    cy.contains('Informations personnelles').should('be.visible')
    cy.get('input[type="email"]').should('have.value', 'admin@padel.com')
    cy.contains('N° de licence').next('input').should('be.disabled')
  })

  it('Permet de modifier les informations personnelles', () => {
    cy.contains('Prénom').next('input').clear().type('Jean')
    cy.contains('Nom').next('input').clear().type('Dupont')
    cy.contains('Date de naissance').next('input').type('1990-01-01')
    cy.contains('Enregistrer').click()
    cy.contains('Profil mis à jour avec succès').should('be.visible')

    cy.reload()
    cy.contains('Prénom').next('input').should('have.value', 'Jean')
    cy.contains('Nom').next('input').should('have.value', 'Dupont')
  })

  it('Valide les champs du formulaire de profil (Format)', () => {
    // Invalid Firstname
    cy.contains('Prénom').next('input').clear().type('Jean123')
    cy.contains('Enregistrer').click()
    cy.contains('Le prénom contient des caractères invalides').should('be.visible')
    cy.contains('button', 'Fermer').click()

    // Short Firstname
    cy.contains('Prénom').next('input').clear().type('J')
    cy.contains('Enregistrer').click()
    cy.contains('Le prénom doit faire entre 2 et 50 caractères').should('be.visible')
    cy.contains('button', 'Fermer').click()

    // Invalid Lastname
    cy.contains('Prénom').next('input').clear().type('Jean') // Reset valid
    cy.contains('Nom').next('input').clear().type('Dupont!')
    cy.contains('Enregistrer').click()
    cy.contains('Le nom contient des caractères invalides').should('be.visible')
    cy.contains('button', 'Fermer').click()

    // Invalid Email
    cy.contains('Nom').next('input').clear().type('Dupont') // Reset valid
    cy.get('input[name="email"]').clear().type('invalid-email')
    cy.contains('Enregistrer').click()
    cy.contains("Format d'email invalide").should('be.visible')
    cy.contains('button', 'Fermer').click()
  })

  it('Permet de changer le mot de passe', () => {
    cy.contains('Sécurité').click()
    cy.contains('Mot de passe actuel').next('input').type('Test@2025_2026')
    cy.contains('Nouveau mot de passe').next('input').type('NewPass123!@#')
    cy.contains('Confirmer le mot de passe').next('input').type('NewPass123!@#')
    cy.contains('Modifier le mot de passe').click()
    cy.contains('Mot de passe modifié avec succès').should('be.visible')

    // Vérification connexion
    cy.contains('Déconnexion').click()
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('NewPass123!@#')
    cy.get('button[type="submit"]').click()
    cy.url().should('eq', 'http://localhost:5173/')

    // Reset password
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
    cy.get('input[type="file"]').should('exist')
  })
})

describe('Profile Validation', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/profile')
  })

  it('should allow updating profile without changing email', () => {
    cy.get('input[name="firstname"]').clear().type('AdminUpdated')
    cy.contains('button', 'Enregistrer').click()

    cy.reload()
    cy.get('input[name="firstname"]').should('have.value', 'AdminUpdated')

    // Revert
    cy.get('input[name="firstname"]').clear().type('Admin')
    cy.contains('button', 'Enregistrer').click()
  })

  it('should reject future birthdate', () => {
    const futureDate = '2050-01-01'
    cy.get('input[name="birthdate"]').type(futureDate)
    cy.contains('button', 'Enregistrer').click()
    
    cy.contains('Impossible de sélectionner une date future').should('be.visible')
    cy.contains('button', 'Fermer').click()
  })

  it('should reject user under 16', () => {
    const today = new Date()
    const under16Year = today.getFullYear() - 10
    const under16Date = `${under16Year}-01-01`
    
    cy.get('input[name="birthdate"]').type(under16Date)
    cy.contains('button', 'Enregistrer').click()
    
    cy.contains("L'utilisateur doit avoir au moins 16 ans").should('be.visible')
    cy.contains('button', 'Fermer').click()
  })

  it('should reject email already used', () => {
    // 1. Create another user via API
    cy.window().then((win) => {
      const token = win.localStorage.getItem('token')
      cy.request({
        method: 'GET',
        url: 'http://localhost:8000/api/v1/admin/players',
        headers: { 'Authorization': `Bearer ${token}` }
      }).then((response) => {
        const player = response.body[0]
        cy.request({
          method: 'POST',
          url: 'http://localhost:8000/api/v1/admin/accounts',
          headers: { 'Authorization': `Bearer ${token}` },
          body: { player_id: player.id },
          failOnStatusCode: false // In case it already exists
        }).then(() => {
          // 2. Try to use this email
          cy.get('input[name="email"]').clear().type(player.email)
          cy.contains('button', 'Enregistrer').click()
          cy.contains('Cet email est déjà utilisé').should('be.visible')
          cy.contains('button', 'Fermer').click()
        })
      })
    })
  })

  it('should reject large profile picture', () => {
    // Create a large file (3MB)
    const largeFile = Cypress.Buffer.alloc(3 * 1024 * 1024)
    cy.get('input[type="file"]').selectFile({
      contents: largeFile,
      fileName: 'large.jpg',
      mimeType: 'image/jpeg'
    }, { force: true })

    cy.contains('La taille du fichier ne doit pas dépasser 2MB').should('be.visible')
  })
})
