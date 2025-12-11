describe('Admin Delete Protection', () => {
  beforeEach(() => {
    cy.login('admin@padel.com', 'Test@2025_2026')
    cy.visit('/admin')
    cy.contains('button', 'Joueurs').click()
  })

  it('should prevent deleting own account', () => {
    const timestamp = Date.now()
    const email = `admin${timestamp}@test.com`
    const firstname = 'Admin'
    const lastname = 'Test'
    const fullname = `${firstname} ${lastname}`
    
    // 1. Create a new player who will become admin
    cy.contains('Ajouter un joueur').click()
    cy.get('input[placeholder="Prénom"]').type(firstname)
    cy.get('input[placeholder="Nom"]').type(lastname)
    cy.get('input[placeholder="Entreprise"]').type('Test Corp')
    cy.get('input[type="email"]').type(email)
    cy.get('input[placeholder="N° Licence (LXXXXXX)"]').type(`L${timestamp.toString().slice(-6)}`)
    cy.contains('button', 'Enregistrer').click()
    cy.contains('h3', 'Ajouter un joueur').should('not.exist')

    // 2. Create account for this player
    cy.contains('tr', fullname).within(() => {
        cy.contains('Créer compte').click()
    })
    
    // Capture password
    cy.get('.bg-yellow-100').invoke('text').then((tempPassword) => {
        cy.contains('Fermer').click()

        // 3. Promote to Admin
        cy.contains('tr', fullname).within(() => {
            cy.on('window:confirm', () => true)
            cy.contains('Promouvoir Admin').click()
        })
        
        // 4. Logout
        cy.contains('Déconnexion').click()
        
        // 5. Login as new admin
        cy.get('input[type="email"]').type(email)
        cy.get('input[type="password"]').type(tempPassword)
        cy.get('button[type="submit"]').click()
        
        // 6. Change password (forced)
        cy.contains('Changement de mot de passe requis').should('be.visible')
        
        const newPassword = 'NewPassword123!'
        // The modal inputs don't have name attributes in the code I read, just v-model.
        // I'll use labels or order.
        cy.contains('Nouveau mot de passe').parent().find('input').type(newPassword)
        cy.contains('Confirmer le mot de passe').parent().find('input').type(newPassword)
        // Check button text in LoginPage.vue: "Changer le mot de passe" or similar?
        // I need to check LoginPage.vue again for the button text.
        // It's inside the modal form.
        cy.get('form').last().find('button[type="submit"]').click()
        
        // Wait for login to complete (redirect to home)
        cy.url().should('eq', 'http://localhost:5173/')
        
        // 7. Go to Admin > Joueurs
        cy.visit('/admin')
        cy.contains('button', 'Joueurs').click()
        
        // 8. Try to delete self
        cy.contains('tr', fullname).within(() => {
            // Stub alert
            const stub = cy.stub()
            cy.on('window:alert', stub)
            
            cy.contains('Supprimer').click()
            
            // Verify alert
            cy.wrap(stub).should('be.calledWith', 'Impossible de supprimer votre propre compte')
        })
    })
  })
})
