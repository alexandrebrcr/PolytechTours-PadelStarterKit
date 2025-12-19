# ============================================
# FICHIER : backend/tests/test_matches_filter.py
# ============================================

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_matches_company_filter():
    # Login as admin
    login_response = client.post("/api/v1/auth/login", json={
        "email": "admin@padel.com",
        "password": "Test@2025_2026"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create matches with different companies
    # Assuming data is already seeded or we can create it.
    # Let's check existing matches first.
    response = client.get("/api/v1/matches?all_matches=true", headers=headers)
    matches = response.json()
    print(f"Total matches: {len(matches)}")
    
    # Filter by "Dream Team"
    response = client.get("/api/v1/matches?company=Dream%20Team&all_matches=true", headers=headers)
    filtered_matches = response.json()
    print(f"Filtered matches (Dream Team): {len(filtered_matches)}")
    
    for m in filtered_matches:
        t1 = m['team1']
        t2 = m['team2']
        # Check if Dream Team is involved
        is_dream_team = "Dream Team" in t1['name'] or "Dream Team" in t2['name']
        # Or check players companies
        p_companies = [p['company'] for p in t1['players']] + [p['company'] for p in t2['players']]
        is_dream_team_company = any("Dream Team" in c for c in p_companies)
        
        assert is_dream_team or is_dream_team_company

    # Filter by "Equipe 42"
    response = client.get("/api/v1/matches?company=Equipe%2042&all_matches=true", headers=headers)
    filtered_matches_42 = response.json()
    print(f"Filtered matches (Equipe 42): {len(filtered_matches_42)}")

    # Filter by non-existent company
    response = client.get("/api/v1/matches?company=NonExistent&all_matches=true", headers=headers)
    assert len(response.json()) == 0
