# ============================================
# FICHIER : backend/tests/test_name_validation.py
# ============================================

import pytest
from fastapi import status

def test_create_player_valid_names(client, admin_token_headers):
    """Test creation of player with valid special characters in names"""
    data = {
        "firstname": "Jean-Pierre_Test",
        "lastname": "Dupont.De-La_Tour",
        "company": "Test Corp",
        "email": "jp.dupont@test.com",
        "license_number": "L123456"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["firstname"] == "Jean-Pierre_Test"
    assert response.json()["lastname"] == "Dupont.De-La_Tour"

def test_create_player_invalid_firstname_dot(client, admin_token_headers):
    """Test creation of player with dot in firstname (should fail)"""
    data = {
        "firstname": "Jean.Pierre",
        "lastname": "Dupont",
        "company": "Test Corp",
        "email": "jp.fail@test.com",
        "license_number": "L123457"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_player_invalid_digits(client, admin_token_headers):
    """Test creation of player with digits (should fail)"""
    data = {
        "firstname": "Jean123",
        "lastname": "Dupont",
        "company": "Test Corp",
        "email": "jp.digits@test.com",
        "license_number": "L123458"
    }
    response = client.post("/api/v1/admin/players", json=data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_profile_valid_names(client, test_user, user_token_headers):
    """Test profile update with valid special characters"""
    update_data = {
        "firstname": "Marie-Claire_Test",
        "lastname": "Martin.Du-Gard",
        "email": test_user.email
    }
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["firstname"] == "Marie-Claire_Test"
    assert response.json()["lastname"] == "Martin.Du-Gard"

def test_update_profile_invalid_firstname_dot(client, test_user, user_token_headers):
    """Test profile update with dot in firstname (should fail)"""
    update_data = {
        "firstname": "Marie.Claire",
        "lastname": "Martin",
        "email": test_user.email
    }
    response = client.put("/api/v1/auth/me", json=update_data, headers=user_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
