import pytest
from fastapi import status
import os
from app.models.models import User

def test_get_profile(client, test_user, user_token_headers):
    """Test récupération du profil utilisateur"""
    response = client.get("/api/v1/auth/me", headers=user_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role
    assert "firstname" in data
    assert "lastname" in data

def test_update_profile_success(client, test_user, user_token_headers):
    """Test mise à jour du profil avec données valides"""
    update_data = {
        "firstname": "Jean",
        "lastname": "Dupont",
        "email": "jean.dupont@example.com",
        "birthdate": "1990-01-01"
    }
    
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["firstname"] == "Jean"
    assert data["lastname"] == "Dupont"
    assert data["email"] == "jean.dupont@example.com"
    assert data["birthdate"] == "1990-01-01"

def test_update_profile_invalid_age(client, test_user, user_token_headers):
    """Test mise à jour avec âge < 16 ans"""
    from datetime import date
    today = date.today()
    too_young = f"{today.year - 15}-01-01"
    
    update_data = {
        "firstname": "Jean",
        "lastname": "Dupont",
        "email": test_user.email,
        "birthdate": too_young
    }
    
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Note: Pydantic validation error structure

def test_update_profile_invalid_name(client, test_user, user_token_headers):
    """Test mise à jour avec caractères invalides dans le nom"""
    update_data = {
        "firstname": "Jean123",  # Chiffres interdits
        "lastname": "Dupont",
        "email": test_user.email,
        "birthdate": "1990-01-01"
    }
    
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_profile_email_conflict(client, test_user, user_token_headers, db_session):
    """Test mise à jour avec email déjà existant"""
    # Créer un autre utilisateur
    other_user = User(
        email="other@example.com",
        password_hash="hash",
        role="JOUEUR",
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()
    
    update_data = {
        "firstname": "Jean",
        "lastname": "Dupont",
        "email": "other@example.com",  # Email déjà pris
        "birthdate": "1990-01-01"
    }
    
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "déjà utilisé" in response.json()["detail"]

def test_upload_avatar_success(client, test_user, user_token_headers):
    """Test upload d'avatar réussi"""
    # Créer une fausse image
    file_content = b"fake image content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    response = client.post("/api/v1/auth/me/avatar", files=files, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile_picture"] is not None
    assert "static/uploads" in data["profile_picture"]
    
    # Nettoyage (optionnel si on utilise un dossier temporaire ou mock)
    # Dans un vrai test, on mockerait le système de fichiers ou on nettoierait après

def test_upload_avatar_invalid_format(client, test_user, user_token_headers):
    """Test upload avec mauvais format"""
    file_content = b"fake text content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    
    response = client.post("/api/v1/auth/me/avatar", files=files, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Format de fichier non supporté" in response.json()["detail"]

def test_delete_avatar(client, test_user, user_token_headers):
    """Test suppression d'avatar"""
    # D'abord uploader ou définir un avatar
    test_user.profile_picture = "/static/uploads/test.jpg"
    
    response = client.delete("/api/v1/auth/me/avatar", headers=user_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile_picture"] is None

def test_change_password_success(client, test_user, user_token_headers):
    """Test changement de mot de passe réussi"""
    # Le mot de passe initial est "ValidP@ssw0rd123" (défini dans conftest.py probablement)
    # On suppose que le conftest configure un user avec un mot de passe connu
    
    # Note: Il faut s'assurer que le conftest.py configure bien le mot de passe
    # Si on ne connait pas le mot de passe, on peut le resetter dans le test
    from app.core.security import get_password_hash
    test_user.password_hash = get_password_hash("OldPassword123!")
    
    data = {
        "current_password": "OldPassword123!",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }
    
    response = client.post("/api/v1/auth/change-password", json=data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Mot de passe modifié avec succès"

def test_change_password_wrong_current(client, test_user, user_token_headers):
    """Test changement avec mauvais mot de passe actuel"""
    data = {
        "current_password": "WrongPassword123!",
        "new_password": "NewPassword123!",
        "confirm_password": "NewPassword123!"
    }
    
    response = client.post("/api/v1/auth/change-password", json=data, headers=user_token_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "incorrect" in response.json()["detail"]
