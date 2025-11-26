import pytest
from datetime import date, timedelta
from app.models.models import Match, Team, Player, MatchStatus, Event

@pytest.fixture
def ranking_data(db_session):
    """Crée des données pour tester le classement"""
    # Créer 3 équipes
    t1 = Team(company="Company A")
    t2 = Team(company="Company B")
    t3 = Team(company="Company C")
    db_session.add_all([t1, t2, t3])
    db_session.commit()
    
    # Créer un événement
    event = Event(date=date.today(), start_time="10:00:00")
    db_session.add(event)
    db_session.commit()
    
    # Match 1: A bat B (6-4, 6-4) -> A: 3pts, +2 sets | B: 0pts, -2 sets
    m1 = Match(
        event_id=event.id, court_number=1,
        team1_id=t1.id, team2_id=t2.id,
        status=MatchStatus.TERMINE,
        score_team1="6-4, 6-4"
    )
    
    # Match 2: C bat A (4-6, 6-4, 6-4) -> C: 3pts, +1 set | A: 0pts, -1 set
    m2 = Match(
        event_id=event.id, court_number=2,
        team1_id=t1.id, team2_id=t3.id,
        status=MatchStatus.TERMINE,
        score_team1="6-4, 4-6, 4-6" # Score vu par Team 1 (A)
    )
    
    # Match 3: B bat C (6-0, 6-0) -> B: 3pts, +2 sets | C: 0pts, -2 sets
    m3 = Match(
        event_id=event.id, court_number=3,
        team1_id=t2.id, team2_id=t3.id,
        status=MatchStatus.TERMINE,
        score_team1="6-0, 6-0" # Score vu par Team 1 (B)
    )
    
    db_session.add_all([m1, m2, m3])
    db_session.commit()
    
    return t1, t2, t3

def test_get_ranking(client, user_token_headers, ranking_data):
    """Test le calcul du classement"""
    response = client.get("/api/v1/results/ranking", headers=user_token_headers)
    assert response.status_code == 200
    ranking = response.json()
    
    assert len(ranking) == 3
    
    # Calculs attendus :
    # A: 1V, 1D, 3pts. Sets: +2 -1 = +1
    # B: 1V, 1D, 3pts. Sets: -2 +2 = 0
    # C: 1V, 1D, 3pts. Sets: +1 -2 = -1
    
    # Ordre attendu : A (1er), B (2ème), C (3ème) car égalité de points et victoires, départagé par diff sets
    assert ranking[0]["company"] == "Company A"
    assert ranking[0]["points"] == 3
    assert ranking[0]["sets_won"] - ranking[0]["sets_lost"] == 1
    
    assert ranking[1]["company"] == "Company B"
    assert ranking[1]["points"] == 3
    assert ranking[1]["sets_won"] - ranking[1]["sets_lost"] == 0
    
    assert ranking[2]["company"] == "Company C"
    assert ranking[2]["points"] == 3
    assert ranking[2]["sets_won"] - ranking[2]["sets_lost"] == -1

def test_score_validation_valid(client, admin_token_headers, ranking_data):
    """Test la validation d'un score valide"""
    # On utilise un match existant pour tester l'update
    # On va créer un nouveau match A_VENIR pour le tester
    # Mais ici on teste juste le validateur via l'API update
    
    # Créer un match A_VENIR
    response = client.post("/api/v1/matches/", headers=admin_token_headers, json={
        "date": (date.today() + timedelta(days=1)).isoformat(),
        "time": "12:00:00",
        "court_number": 4,
        "team1_id": ranking_data[0].id,
        "team2_id": ranking_data[1].id
    })
    match_id = response.json()["id"]
    
    # Update avec score valide
    res = client.put(f"/api/v1/matches/{match_id}", headers=admin_token_headers, json={
        "status": "TERMINE",
        "score_team1": "6-4, 3-6, 7-5"
    })
    assert res.status_code == 200
    assert res.json()["score_team1"] == "6-4, 3-6, 7-5"

def test_score_validation_invalid_format(client, admin_token_headers, ranking_data):
    """Test score invalide (format)"""
    # Créer match
    response = client.post("/api/v1/matches/", headers=admin_token_headers, json={
        "date": (date.today() + timedelta(days=2)).isoformat(),
        "time": "12:00:00",
        "court_number": 5,
        "team1_id": ranking_data[0].id,
        "team2_id": ranking_data[1].id
    })
    match_id = response.json()["id"]
    
    invalid_scores = [
        "6-4 6-3", # Manque virgule
        "6-4, 6",  # Set incomplet
        "A-B",     # Pas des chiffres
        "6-4, 6-4, 6-4, 6-4" # Trop de sets
    ]
    
    for score in invalid_scores:
        res = client.put(f"/api/v1/matches/{match_id}", headers=admin_token_headers, json={
            "status": "TERMINE",
            "score_team1": score
        })
        assert res.status_code == 422

def test_score_validation_invalid_rules(client, admin_token_headers, ranking_data):
    """Test score invalide (règles tennis/padel)"""
    response = client.post("/api/v1/matches/", headers=admin_token_headers, json={
        "date": (date.today() + timedelta(days=3)).isoformat(),
        "time": "12:00:00",
        "court_number": 6,
        "team1_id": ranking_data[0].id,
        "team2_id": ranking_data[1].id
    })
    match_id = response.json()["id"]
    
    invalid_scores = [
        "5-4",      # Pas fini (faut 6 jeux)
        "7-0",      # Impossible (max 6-0 ou 7-5/7-6)
        "6-5",      # Pas fini (faut 2 jeux d'écart ou 7-6)
        "8-6"       # Impossible (max 7)
    ]
    
    for score in invalid_scores:
        res = client.put(f"/api/v1/matches/{match_id}", headers=admin_token_headers, json={
            "status": "TERMINE",
            "score_team1": score
        })
        assert res.status_code == 422
