import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "role": "user"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"

def test_login(client, test_user):
    response = client.post(
        "/token",
        data={
            "username": "test@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, user_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com" 