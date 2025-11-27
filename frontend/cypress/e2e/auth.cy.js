describe('Authentification', () => {
  beforeEach(() => {
    // Nettoyer le localStorage
    cy.clearLocalStorage()
    cy.visit('http://localhost:5173')
  })

  it('Affiche la page de login', () => {
    cy.visit('/login')
    cy.contains('Corpo Padel').should('be.visible')
    cy.contains('Connectez-vous à votre compte').should('be.visible')
    cy.get('input[type="email"]').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
  })

  it('Connexion réussie avec credentials valides', () => {
    cy.visit('/login')
    
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier la redirection vers la page d'accueil
    cy.url().should('eq', 'http://localhost:5173/')
    // Bonjour a été retiré, on affiche directement l'identifiant
    // Comme on a mis "Admin System" dans init_db, on doit voir ça
    cy.contains('Admin System').should('be.visible')
  })

  it('Connexion échoue avec email invalide', () => {
    cy.visit('/login')
    
    const randomEmail = `wrong_${Date.now()}@example.com`
    cy.get('input[type="email"]').type(randomEmail)
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier le message d'erreur
    cy.contains('Email ou mot de passe incorrect').should('be.visible')
    cy.contains('Tentatives restantes').should('be.visible')
  })

  it('Connexion échoue avec mot de passe invalide', () => {
    cy.visit('/login')
    
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('WrongPassword')
    cy.get('button[type="submit"]').click()
    
    // Vérifier le message d'erreur
    cy.contains('Email ou mot de passe incorrect').should('be.visible')
  })

  it('Bloque le compte après 5 tentatives échouées', () => {
    cy.visit('/login')
    
    const lockedEmail = `locked_${Date.now()}@test.com`
    
    // Faire 4 tentatives échouées (compte passe à 4 tentatives)
    for (let i = 0; i < 4; i++) {
      cy.get('input[type="email"]').clear().type(lockedEmail)
      cy.get('input[type="password"]').clear().type('WrongPassword')
      cy.get('button[type="submit"]').click()
      cy.contains('Email ou mot de passe incorrect').should('be.visible')
    }

    // 5ème tentative : doit bloquer
    cy.get('input[type="email"]').clear().type(lockedEmail)
    cy.get('input[type="password"]').clear().type('WrongPassword')
    cy.get('button[type="submit"]').click()
    
    // Vérifier le message de blocage
    cy.contains('Compte bloqué').should('be.visible')
    cy.contains('minutes').should('be.visible')
    cy.get('button[type="submit"]').should('be.disabled')
  })

  it('Redirection automatique si déjà connecté', () => {
    // Se connecter d'abord
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Attendre la redirection
    cy.url().should('eq', 'http://localhost:5173/')
    
    // Essayer d'accéder à /login
    cy.visit('/login')
    
    // Devrait être redirigé vers l'accueil
    cy.url().should('eq', 'http://localhost:5173/')
  })

  it('Déconnexion fonctionne correctement', () => {
    // Se connecter
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Vérifier que l'utilisateur est connecté
    cy.url().should('eq', 'http://localhost:5173/')
    
    // Se déconnecter
    cy.contains('Déconnexion').click()
    
    // Vérifier la redirection vers login
    cy.url().should('include', '/login')
    
    // Vérifier que le token est supprimé
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null
    })
  })

  it('Force le changement de mot de passe à la première connexion', () => {
    const timestamp = Date.now()
    const newEmail = `newuser${timestamp}@test.com`
    const license = `L${timestamp.toString().slice(-6)}` // Ensure 6 digits
    const randomLetters = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5) || 'abcde'
    const firstname = `New${randomLetters}`
    const lastname = `User${randomLetters}`

    // 1. Admin crée le compte
    cy.visit('/login')
    cy.get('input[type="email"]').type('admin@padel.com')
    cy.get('input[type="password"]').type('Admin@2025!')
    cy.get('button[type="submit"]').click()
    
    // Créer joueur
    cy.contains('Administration').click()
    cy.contains('Joueurs').click() // Ensure tab is active
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type(firstname)
    cy.get('input[placeholder="Nom"]').type(lastname)
    cy.get('input[placeholder="Entreprise"]').type('Test Corp')
    cy.get('input[type="email"]').type(newEmail)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(license)
    cy.contains('button', 'Enregistrer').click()
    
    // Créer compte (trouver le bouton dans la ligne du joueur)
    cy.contains('tr', firstname).contains('Créer compte').click()
    
    // Récupérer le mot de passe temporaire
    cy.get('.bg-yellow-100').invoke('text').then((tempPassword) => {
      cy.contains('Fermer').click()
      cy.contains('Déconnexion').click()
      
      // 2. Première connexion du nouvel utilisateur
      cy.get('input[type="email"]').type(newEmail)
      cy.get('input[type="password"]').type(tempPassword)
      cy.get('button[type="submit"]').click()
      
      // 3. Vérifier la modale
      cy.contains('Changement de mot de passe requis').should('be.visible')
      
      // 4. Changer le mot de passe
      const newPass = 'NewPass123!@#'
      // Le premier input password est celui du login (caché par la modale mais présent), 
      // les suivants sont dans la modale
      cy.get('input[type="password"]').eq(1).type(newPass) // Nouveau mdp
      cy.get('input[type="password"]').eq(2).type(newPass) // Confirm
      cy.contains('button', 'Changer le mot de passe').click()
      
      // 5. Vérifier redirection
      cy.url().should('eq', 'http://localhost:5173/')
      // On doit voir le Prénom Nom
      cy.contains(`${firstname} ${lastname}`).should('be.visible')
    })
  })

  it('Affiche la modale de mot de passe oublié', () => {
    cy.visit('/login')
    cy.contains('Mot de passe oublié ?').click()
    cy.contains('Veuillez contacter votre administrateur local').should('be.visible')
    cy.contains('contact.support@padel.com').should('be.visible')
    cy.contains('button', 'Fermer').click()
    cy.contains('Veuillez contacter votre administrateur local').should('not.exist')
  })
})
