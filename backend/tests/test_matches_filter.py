# ============================================
# FICHIER : backend/tests/test_matches_filter.py
# ============================================

import pytest
from datetime import date, timedelta, time
from app.models.models import Match, Team, Player, MatchStatus, Event


@pytest.fixture
def filter_data(db_session):
    """Crée des données pour tester les filtres"""
    # Team Dream Team
    p1 = Player(firstname="P1", lastname="DT", company="Dream Team", email="p1@dt.com", license_number="LDT001")
    p2 = Player(firstname="P2", lastname="DT", company="Dream Team", email="p2@dt.com", license_number="LDT002")
    t1 = Team(name="Dream Team")
    t1.players = [p1, p2]

    # Team Equipe 42
    p3 = Player(firstname="P3", lastname="E42", company="Equipe 42", email="p3@e42.com", license_number="LE42001")
    p4 = Player(firstname="P4", lastname="E42", company="Equipe 42", email="p4@e42.com", license_number="LE42002")
    t2 = Team(name="Equipe 42")
    t2.players = [p3, p4]

    db_session.add_all([p1, p2, p3, p4, t1, t2])
    db_session.commit()
    
    # Créer un événement
    event = Event(date=date.today() + timedelta(days=5), start_time=time(10, 0))
    db_session.add(event)
    db_session.commit()
    
    # Match Dream Team vs Equipe 42
    m1 = Match(
        event_id=event.id, court_number=1,
        team1_id=t1.id, team2_id=t2.id,
        status=MatchStatus.A_VENIR
    )
    
    db_session.add(m1)
    db_session.commit()
    
    return t1, t2


def test_matches_company_filter(client, admin_token_headers, filter_data):
    headers = admin_token_headers

    # Les données créées dans filter_data contiennent Dream Team vs Equipe 42
    response = client.get("/api/v1/matches?all_matches=true", headers=headers)
    matches = response.json()
    assert len(matches) >= 1  # Au moins notre match créé
    
    # Filter by "Dream Team"
    response = client.get("/api/v1/matches?company=Dream%20Team&all_matches=true", headers=headers)
    filtered_matches = response.json()
    assert len(filtered_matches) >= 1
    
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
    assert len(filtered_matches_42) >= 1

    # Filter by non-existent company
    response = client.get("/api/v1/matches?company=NonExistent&all_matches=true", headers=headers)
    assert len(response.json()) == 0
