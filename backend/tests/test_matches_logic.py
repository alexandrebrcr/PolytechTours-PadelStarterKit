# ============================================
# FICHIER : backend/tests/test_matches_logic.py
# ============================================

import pytest
from datetime import date, timedelta, time as time_type
from app.models.models import Match, Team, Player, MatchStatus, Event


@pytest.fixture
def logic_test_data(db_session):
    """Crée des données pour tester la logique des matchs"""
    # Team 1
    p1 = Player(firstname="Logic", lastname="P1", company="Logic Co", email="lp1@logic.com", license_number="LLOG001")
    p2 = Player(firstname="Logic", lastname="P2", company="Logic Co", email="lp2@logic.com", license_number="LLOG002")
    t1 = Team(name="Logic Team 1")
    t1.players = [p1, p2]

    # Team 2
    p3 = Player(firstname="Logic", lastname="P3", company="Logic Co", email="lp3@logic.com", license_number="LLOG003")
    p4 = Player(firstname="Logic", lastname="P4", company="Logic Co", email="lp4@logic.com", license_number="LLOG004")
    t2 = Team(name="Logic Team 2")
    t2.players = [p3, p4]

    db_session.add_all([p1, p2, p3, p4, t1, t2])
    db_session.commit()
    
    return t1, t2


def test_update_match_status_logic(client, admin_token_headers, logic_test_data):
    headers = admin_token_headers
    t1, t2 = logic_test_data

    # 1. Create a match
    match_data = {
        "date": (date.today() + timedelta(days=10)).isoformat(),
        "time": "10:00",
        "court_number": 1,
        "team1_id": t1.id,
        "team2_id": t2.id
    }
    
    create_res = client.post("/api/v1/matches/", json=match_data, headers=headers)
    assert create_res.status_code == 200
    match_id = create_res.json()["id"]

    # 2. Try to set status to TERMINE without scores -> Should fail
    update_res = client.put(f"/api/v1/matches/{match_id}", json={"status": "TERMINE"}, headers=headers)
    assert update_res.status_code == 400
    assert "Impossible de terminer un match sans scores" in update_res.json()["detail"]

    # 3. Set status to TERMINE with scores -> Should succeed
    valid_score = "6-0, 6-0"
    update_res = client.put(f"/api/v1/matches/{match_id}", json={
        "status": "TERMINE",
        "score_team1": valid_score,
        "score_team2": valid_score 
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "TERMINE"
    assert update_res.json()["score_team1"] == valid_score

    # 4. Change status back to A_VENIR -> Scores should be cleared
    update_res = client.put(f"/api/v1/matches/{match_id}", json={"status": "A_VENIR"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "A_VENIR"
    assert update_res.json()["score_team1"] is None
    assert update_res.json()["score_team2"] is None

    # 5. Change time without status -> Should work (and not fail with None error)
    update_res = client.put(f"/api/v1/matches/{match_id}", json={"time": "12:00"}, headers=headers)
    assert update_res.status_code == 200, f"Update failed: {update_res.text}"
    assert update_res.json()["time"] == "12:00:00"

