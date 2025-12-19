
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import MatchStatus
from datetime import date, timedelta
import random

client = TestClient(app)

def test_update_match_status_logic():
    # Login as admin
    login_response = client.post("/api/v1/auth/login", json={
        "email": "admin@padel.com",
        "password": "Test@2025_2026"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a match
    # Use a random court (1-10) and random date offset to avoid conflicts
    court_num = random.randint(1, 10)
    days_offset = random.randint(1, 100)
    match_data = {
        "date": (date.today() + timedelta(days=days_offset)).isoformat(),
        "time": "10:00",
        "court_number": court_num,
        "team1_id": 1, # Assuming seeded teams
        "team2_id": 2
    }
    # Need to get valid team IDs first
    teams = client.get("/api/v1/admin/teams", headers=headers).json()
    if len(teams) >= 2:
        match_data["team1_id"] = teams[0]["id"]
        match_data["team2_id"] = teams[1]["id"]
    
    create_res = client.post("/api/v1/matches/", json=match_data, headers=headers)
    assert create_res.status_code == 200
    match_id = create_res.json()["id"]

    # 2. Try to set status to TERMINE without scores -> Should fail
    update_res = client.put(f"/api/v1/matches/{match_id}", json={"status": "TERMINE"}, headers=headers)
    assert update_res.status_code == 400
    assert "Impossible de terminer un match sans scores" in update_res.json()["detail"]

    # 3. Set status to TERMINE with scores -> Should succeed
    update_res = client.put(f"/api/v1/matches/{match_id}", json={
        "status": "TERMINE",
        "score_team1": "6-0, 6-0",
        "score_team2": "0-6, 0-6" # Note: Logic in schema might validate this, let's use valid scores
    }, headers=headers)
    # Wait, schema validation is strict now. "6-0, 6-0" means team 1 won 2 sets.
    # score_team1 is string "6-0, 6-0" ? No, schema says score_team1 is string.
    # Actually the model has score_team1 and score_team2 as strings?
    # Let's check models.py or schema.
    # Schema MatchUpdate has score_team1: str.
    # But wait, usually score is one string "6-4, 6-2".
    # In this project, it seems score_team1 and score_team2 are separate fields?
    # Let's check MatchResponse in matches.py (read earlier).
    # It has score_team1 and score_team2.
    # And MatchUpdate validates them.
    # The validator checks format "d-d, d-d".
    # If score_team1="6-0, 6-0", it means Team 1 won 6-0 and 6-0?
    # The validator logic: sets = v.split(", ").
    # It seems the field `score_team1` holds the FULL score string?
    # Let's re-read the validator in `backend/app/schemas/matches.py`.
    # `def validate_score(cls, v):`
    # It validates `v` which is `score_team1` OR `score_team2`.
    # This implies `score_team1` contains the full match score? That's weird naming.
    # Or maybe `score_team1` is just the score for team 1?
    # But the regex `^\d+-\d+(, \d+-\d+){1,2}$` suggests "6-4, 6-2".
    # If `score_team1` was just "2" (sets won), it wouldn't match.
    # If `score_team1` was "6, 6", it wouldn't match.
    # It seems `score_team1` holds the score string like "6-4, 6-2".
    # But why `score_team2`?
    # Maybe legacy or redundancy?
    # Let's assume we send the same score string to both or just one?
    # The update logic in `api/matches.py`:
    # `if match_in.score_team1 is not None: match.score_team1 = match_in.score_team1`
    # `if match_in.score_team2 is not None: match.score_team2 = match_in.score_team2`
    # And the validation: `if not s1 or not s2: raise ...`
    # So BOTH must be present.
    
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
    # This tests the fix for "Input should be None" if date is not provided
    update_res = client.put(f"/api/v1/matches/{match_id}", json={"time": "12:00"}, headers=headers)
    assert update_res.status_code == 200, f"Update failed: {update_res.text}"
    assert update_res.json()["time"] == "12:00:00"

