# ============================================
# FICHIER : backend/tests/test_matches.py
# ============================================

import pytest
from datetime import date, time, timedelta
from app.models.models import Match, Event, Team, Player, MatchStatus

@pytest.fixture
def test_teams(db_session):
    """Crée des équipes et joueurs pour les tests"""
    # Team 1
    p1 = Player(firstname="John", lastname="Doe", company="Company A", license_number="L000001", email="john@a.com")
    p2 = Player(firstname="Jane", lastname="Doe", company="Company A", license_number="L000002", email="jane@a.com")
    t1 = Team(name="Company A")
    db_session.add_all([p1, p2, t1])
    db_session.commit()
    p1.team_id = t1.id
    p2.team_id = t1.id
    
    # Team 2
    p3 = Player(firstname="Bob", lastname="Smith", company="Company B", license_number="L000003", email="bob@b.com")
    p4 = Player(firstname="Alice", lastname="Smith", company="Company B", license_number="L000004", email="alice@b.com")
    t2 = Team(name="Company B")
    db_session.add_all([p3, p4, t2])
    db_session.commit()
    p3.team_id = t2.id
    p4.team_id = t2.id
    
    db_session.commit()
    return t1, t2

def test_create_match(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() + timedelta(days=1)
    
    response = client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["court_number"] == 1
    assert data["status"] == "A_VENIR"
    assert data["team1"]["name"] == "Company A"

def test_create_match_conflict(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() + timedelta(days=1)
    
    # Premier match
    client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    
    # Second match même créneau même piste
    response = client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    
    assert response.status_code == 400
    assert "déjà prévu" in response.json()["detail"]

def test_create_match_past_date(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() - timedelta(days=1)
    
    response = client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    
    assert response.status_code == 422  # Validation Error

def test_get_matches(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() + timedelta(days=1)
    
    client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    
    response = client.get("/api/v1/matches/", headers=admin_token_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_update_match(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() + timedelta(days=1)
    
    # Créer
    create_res = client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    match_id = create_res.json()["id"]
    
    # Modifier
    response = client.put(
        f"/api/v1/matches/{match_id}",
        headers=admin_token_headers,
        json={
            "court_number": 2
        }
    )
    
    assert response.status_code == 200
    assert response.json()["court_number"] == 2

def test_delete_match(client, admin_token_headers, test_teams):
    t1, t2 = test_teams
    match_date = date.today() + timedelta(days=1)
    
    create_res = client.post(
        "/api/v1/matches/",
        headers=admin_token_headers,
        json={
            "date": match_date.isoformat(),
            "time": "19:00:00",
            "court_number": 1,
            "team1_id": t1.id,
            "team2_id": t2.id
        }
    )
    match_id = create_res.json()["id"]
    
    response = client.delete(f"/api/v1/matches/{match_id}", headers=admin_token_headers)
    assert response.status_code == 200
    
    # Vérifier suppression
    get_res = client.get("/api/v1/matches/", headers=admin_token_headers)
    match_ids = [m["id"] for m in get_res.json()]
    assert match_id not in match_ids
