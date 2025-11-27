describe('Planning Management', () => {
    beforeEach(() => {
        cy.login('admin@padel.com', 'Admin@2025!')
    })

    it('should display planning page', () => {
        cy.visit('/planning')
        cy.contains('h1', 'Planning')
        cy.contains('button', 'Ajouter un événement')
    })

    it('should allow admin to create an event', () => {
        const today = new Date()
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`

        // Mock teams
        cy.intercept('GET', '/api/v1/admin/teams', {
            statusCode: 200,
            body: [
                { id: 1, company: 'Team A', players: [] },
                { id: 2, company: 'Team B', players: [] }
            ]
        }).as('getTeams')

        // Mock create response
        cy.intercept('POST', '/api/v1/planning', (req) => {
            req.reply({
                statusCode: 200,
                body: {
                    id: 999,
                    date: req.body.date,
                    start_time: req.body.start_time,
                    matches: [
                        {
                            id: 100,
                            court_number: req.body.matches[0].court_number,
                            status: 'A_VENIR',
                            team1: { id: 1, company: 'Team A', players: [] },
                            team2: { id: 2, company: 'Team B', players: [] }
                        }
                    ]
                }
            })
        }).as('createEvent')

        // Mock get events refresh - return the created event
        cy.intercept('GET', '/api/v1/planning*', {
            statusCode: 200,
            body: [
                {
                    id: 999,
                    date: dateStr,
                    start_time: '10:00:00',
                    matches: [
                        {
                            id: 100,
                            court_number: 1,
                            status: 'A_VENIR',
                            team1: { id: 1, company: 'Team A', players: [] },
                            team2: { id: 2, company: 'Team B', players: [] }
                        }
                    ]
                }
            ]
        }).as('getEvents')

        cy.visit('/planning')
        cy.contains('button', 'Ajouter un événement').click()
        cy.wait('@getTeams')

        cy.get('input[type="date"]').type(dateStr)
        cy.get('input[type="time"]').type('10:00')

        // Select first match details
        cy.get('.border.p-4').first().within(() => {
            cy.get('select').eq(0).select('1') // Piste 1
            cy.get('select').eq(1).select('Team A')
            cy.get('select').eq(2).select('Team B')
        })

        cy.contains('button', 'Enregistrer').click()
        cy.wait('@createEvent')
        cy.wait('@getEvents')

        // Verify event appears on the calendar
        cy.contains('10:00').should('be.visible')
        cy.contains('1 match(s)').should('be.visible')
    })

    it('should allow admin to delete an event', () => {
        const today = new Date()
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`

        // Mock initial events with one event
        cy.intercept('GET', '/api/v1/planning*', {
            statusCode: 200,
            body: [
                {
                    id: 999,
                    date: dateStr,
                    start_time: '10:00:00',
                    matches: [
                        {
                            id: 100,
                            court_number: 1,
                            status: 'A_VENIR',
                            team1: { id: 1, company: 'Team A', players: [] },
                            team2: { id: 2, company: 'Team B', players: [] }
                        }
                    ]
                }
            ]
        }).as('getEvents')

        cy.intercept('DELETE', '/api/v1/planning/999', {
            statusCode: 200,
            body: { message: "Event deleted" }
        }).as('deleteEvent')

        cy.visit('/planning')
        cy.wait('@getEvents')

        // Click on the event to open details
        cy.contains('1 match(s)').click()

        // Prepare for the refresh after delete
        cy.intercept('GET', '/api/v1/planning*', {
            statusCode: 200,
            body: []
        }).as('getEventsEmpty')

        // Click delete button in modal
        cy.contains('button', 'Supprimer').click()

        cy.wait('@deleteEvent')
        cy.wait('@getEventsEmpty')

        // Check UI
        cy.contains('1 match(s)').should('not.exist')
    })
})
