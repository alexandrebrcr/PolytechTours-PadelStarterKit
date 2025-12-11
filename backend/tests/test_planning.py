# ============================================
# FICHIER : backend/tests/test_planning.py
# ============================================

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.models import Event, Match, MatchStatus, Team, Player
from datetime import date, timedelta, time
import pytest

@pytest.fixture
def test_teams(db_session):
    teams = []
    for i in range(4):
        team = Team(company=f"Company {i}")
        db_session.add(team)
        teams.append(team)
    db_session.commit()
    for t in teams:
        db_session.refresh(t)
    return teams

def test_create_event_admin(client: TestClient, admin_token_headers, db_session: Session, test_teams):
    # Create event with 2 matches
    team1, team2, team3, team4 = test_teams
    
    data = {
        "date": (date.today() + timedelta(days=10)).isoformat(),
        "start_time": "14:00:00",
        "matches": [
            {
                "court_number": 1,
                "team1_id": team1.id,
                "team2_id": team2.id
            },
            {
                "court_number": 2,
                "team1_id": team3.id,
                "team2_id": team4.id
            }
        ]
    }
    
    response = client.post("/api/v1/planning/", json=data, headers=admin_token_headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["date"] == data["date"]
    assert len(res_data["matches"]) == 2

def test_create_event_conflict(client: TestClient, admin_token_headers, db_session: Session, test_teams):
    team1, team2, team3, team4 = test_teams
    event_date = (date.today() + timedelta(days=11)).isoformat()
    
    # First event
    data1 = {
        "date": event_date,
        "start_time": "10:00:00",
        "matches": [
            { "court_number": 1, "team1_id": team1.id, "team2_id": team2.id }
        ]
    }
    client.post("/api/v1/planning/", json=data1, headers=admin_token_headers)
    
    # Second event same time same court
    data2 = {
        "date": event_date,
        "start_time": "10:00:00",
        "matches": [
            { "court_number": 1, "team1_id": team3.id, "team2_id": team4.id }
        ]
    }
    response = client.post("/api/v1/planning/", json=data2, headers=admin_token_headers)
    assert response.status_code == 400
    assert "déjà occupée" in response.json()["detail"]

def test_create_event_validation(client: TestClient, admin_token_headers, db_session: Session, test_teams):
    team1, team2, team3, team4 = test_teams
    
    # Past date
    data = {
        "date": (date.today() - timedelta(days=1)).isoformat(),
        "start_time": "10:00:00",
        "matches": [{ "court_number": 1, "team1_id": team1.id, "team2_id": team2.id }]
    }
    response = client.post("/api/v1/planning/", json=data, headers=admin_token_headers)
    assert response.status_code == 422
    
    # Same team in one match
    data["date"] = (date.today() + timedelta(days=1)).isoformat()
    data["matches"][0]["team2_id"] = team1.id
    response = client.post("/api/v1/planning/", json=data, headers=admin_token_headers)
    assert response.status_code == 422

    # Same team in multiple matches
    data["matches"] = [
        { "court_number": 1, "team1_id": team1.id, "team2_id": team2.id },
        { "court_number": 2, "team1_id": team1.id, "team2_id": team3.id }
    ]
    response = client.post("/api/v1/planning/", json=data, headers=admin_token_headers)
    assert response.status_code == 422

def test_get_events(client: TestClient, user_token_headers):
    response = client.get("/api/v1/planning/", headers=user_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_event(client: TestClient, admin_token_headers, db_session: Session, test_teams):
    team1, team2, _, _ = test_teams
    
    # Create event
    data = {
        "date": (date.today() + timedelta(days=20)).isoformat(),
        "start_time": "16:00:00",
        "matches": [{ "court_number": 1, "team1_id": team1.id, "team2_id": team2.id }]
    }
    res = client.post("/api/v1/planning/", json=data, headers=admin_token_headers)
    event_id = res.json()["id"]
    
    # Delete
    response = client.delete(f"/api/v1/planning/{event_id}", headers=admin_token_headers)
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get("/api/v1/planning/", headers=admin_token_headers)
    events = response.json()
    assert not any(e["id"] == event_id for e in events)

