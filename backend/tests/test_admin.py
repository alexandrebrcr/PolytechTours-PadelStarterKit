# ============================================
# FICHIER : backend/tests/test_admin.py
# ============================================

import pytest
from fastapi import status
from app.models.models import Player, Team, Pool, User
from app.core.security import verify_password

# --- Players Tests ---

def test_create_player_admin(client, admin_token_headers):
    """Test création joueur par admin"""
    data = {
        "firstname": "Roger",
        "lastname": "Federer",
        "company": "Rolex",
        "email": "roger@rolex.com",
        "license_number": "L123456"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "roger@rolex.com"

def test_create_player_user_forbidden(client, user_token_headers):
    """Test création joueur par user standard (interdit)"""
    data = {
        "firstname": "Novak",
        "lastname": "Djokovic",
        "company": "Lacoste",
        "email": "novak@lacoste.com",
        "license_number": "L654321"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=user_token_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_player_invalid_license(client, admin_token_headers):
    """Test création joueur avec licence invalide"""
    data = {
        "firstname": "Rafa",
        "lastname": "Nadal",
        "company": "Kia",
        "email": "rafa@kia.com",
        "license_number": "INVALID"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_player(client, admin_token_headers, db_session):
    """Test modification joueur"""
    # Créer un joueur d'abord
    player = Player(firstname="Andy", lastname="Murray", company="Head", email="andy@head.com", license_number="L111111")
    db_session.add(player)
    db_session.commit()
    
    update_data = {"company": "Castore"}
    response = client.put(f"/api/v1/admin/players/{player.id}", json=update_data, headers=admin_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["company"] == "Castore"

def test_delete_player(client, admin_token_headers, db_session):
    """Test suppression joueur"""
    player = Player(firstname="Stan", lastname="Wawrinka", company="Yonex", email="stan@yonex.com", license_number="L222222")
    db_session.add(player)
    db_session.commit()
    
    response = client.delete(f"/api/v1/admin/players/{player.id}", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Vérifier qu'il n'existe plus
    assert db_session.query(Player).filter(Player.id == player.id).first() is None

# --- Teams Tests ---

def test_create_team_success(client, admin_token_headers, db_session):
    """Test création équipe valide"""
    # Créer 2 joueurs de la même entreprise
    p1 = Player(firstname="Pierre", lastname="LeGrand", company="CorpA", email="p1@a.com", license_number="L000001")
    p2 = Player(firstname="Paul", lastname="LePetit", company="CorpA", email="p2@a.com", license_number="L000002")
    db_session.add_all([p1, p2])
    db_session.commit()
    
    data = {
        "company": "CorpA",
        "player1_id": p1.id,
        "player2_id": p2.id
    }
    response = client.post("/api/v1/admin/teams", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["company"] == "CorpA"

def test_create_team_different_companies(client, admin_token_headers, db_session):
    """Test création équipe avec entreprises différentes"""
    p1 = Player(firstname="Pierre", lastname="LeGrand", company="CorpA", email="p1@diff.com", license_number="L000003")
    p2 = Player(firstname="Paul", lastname="LePetit", company="CorpB", email="p2@diff.com", license_number="L000004")
    db_session.add_all([p1, p2])
    db_session.commit()
    
    data = {
        "company": "CorpA",
        "player1_id": p1.id,
        "player2_id": p2.id
    }
    response = client.post("/api/v1/admin/teams", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# --- Pools Tests ---

def test_create_pool_success(client, admin_token_headers, db_session):
    """Test création poule valide (6 équipes)"""
    team_ids = []
    # Créer 6 équipes
    for i in range(6):
        suffix = ["Un", "Deux", "Trois", "Quatre", "Cinq", "Six"][i]
        p1 = Player(firstname=f"Pierre {suffix}", lastname="LeGrand", company=f"C{i}", email=f"p1_{i}@c.com", license_number=f"L00001{i}")
        p2 = Player(firstname=f"Paul {suffix}", lastname="LePetit", company=f"C{i}", email=f"p2_{i}@c.com", license_number=f"L00002{i}")
        db_session.add_all([p1, p2])
        db_session.commit()
        
        team = Team(company=f"C{i}")
        db_session.add(team)
        db_session.commit()
        
        p1.team_id = team.id
        p2.team_id = team.id
        team_ids.append(team.id)
    
    db_session.commit()
    
    data = {
        "name": "Poule A",
        "team_ids": team_ids
    }
    response = client.post("/api/v1/admin/pools", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["teams"]) == 6

def test_create_pool_invalid_count(client, admin_token_headers):
    """Test création poule avec mauvais nombre d'équipes"""
    data = {
        "name": "Poule B",
        "team_ids": [1, 2, 3] # Seulement 3 équipes
    }
    response = client.post("/api/v1/admin/pools", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# --- Accounts Tests ---

def test_create_account(client, admin_token_headers, db_session):
    """Test création compte pour joueur"""
    player = Player(firstname="Account", lastname="Test", company="Tech", email="acc@tech.com", license_number="L999999")
    db_session.add(player)
    db_session.commit()
    
    data = {"player_id": player.id}
    response = client.post("/api/v1/admin/accounts", json=data, headers=admin_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert "temp_password" in response.json()
    assert response.json()["email"] == "acc@tech.com"

# --- Role Management Tests ---

def test_change_player_role(client, admin_token_headers, db_session):
    """Test promotion d'un joueur en admin"""
    # Créer un joueur avec un compte
    player = Player(firstname="Role", lastname="Test", company="Test", email="role@test.com", license_number="L888888")
    db_session.add(player)
    db_session.commit()
    
    # Créer le compte utilisateur associé
    user = User(
        email=player.email,
        password_hash="hash",
        role="JOUEUR",
        player_id=player.id
    )
    db_session.add(user)
    db_session.commit()
    
    # Promouvoir
    response = client.put(
        f"/api/v1/admin/players/{player.id}/role",
        json={"role": "ADMINISTRATEUR"},
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    db_session.refresh(user)
    assert user.role == "ADMINISTRATEUR"
    
    # Rétrograder
    response = client.put(
        f"/api/v1/admin/players/{player.id}/role",
        json={"role": "JOUEUR"},
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    db_session.refresh(user)
    assert user.role == "JOUEUR"

def test_change_role_no_account(client, admin_token_headers, db_session):
    """Test changement rôle sur joueur sans compte"""
    player = Player(firstname="No", lastname="Account", company="Test", email="no@acc.com", license_number="L777777")
    db_session.add(player)
    db_session.commit()
    
    response = client.put(
        f"/api/v1/admin/players/{player.id}/role",
        json={"role": "ADMINISTRATEUR"},
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# --- Security Flow Tests ---

def test_account_creation_force_password_change(client, admin_token_headers, db_session):
    """Test que le compte créé doit changer de mot de passe"""
    player = Player(firstname="Flow", lastname="Test", company="Flow", email="flow@test.com", license_number="L666666")
    db_session.add(player)
    db_session.commit()
    
    # 1. Admin crée le compte
    response = client.post("/api/v1/admin/accounts", json={"player_id": player.id}, headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    temp_password = data["temp_password"]
    
    # 2. Vérifier flag en base
    user = db_session.query(User).filter(User.email == player.email).first()
    assert user.must_change_password is True
    
    # 3. User se connecte
    login_response = client.post("/api/v1/auth/login", json={
        "email": player.email,
        "password": temp_password
    })
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    assert login_response.json()["user"]["must_change_password"] is True
    
    # 4. User change son mot de passe
    new_password = "NewPassword123!"
    headers = {"Authorization": f"Bearer {token}"}
    change_pwd_response = client.post("/api/v1/auth/change-password", json={
        "current_password": temp_password,
        "new_password": new_password,
        "confirm_password": new_password
    }, headers=headers)
    assert change_pwd_response.status_code == status.HTTP_200_OK
    
    # 5. Vérifier flag mis à jour
    db_session.refresh(user)
    assert user.must_change_password is False
    
    # 6. Vérifier nouvelle connexion
    login_response_2 = client.post("/api/v1/auth/login", json={
        "email": player.email,
        "password": new_password
    })
    assert login_response_2.status_code == status.HTTP_200_OK
    assert login_response_2.json()["user"]["must_change_password"] is False
