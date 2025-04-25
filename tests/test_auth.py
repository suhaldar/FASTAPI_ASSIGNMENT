import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.models.user import UserRole

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

def test_register_user_invalid_email(client):
    """Test registration with invalid email."""
    response = client.post(
        "/register",
        json={
            "email": "invalid-email",
            "password": "password123",
            "role": "user"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_weak_password(client):
    """Test registration with weak password."""
    response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "123",  # too short
            "role": "user"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_invalid_role(client):
    """Test registration with invalid role."""
    response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "role": "invalid_role"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post("/token")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 