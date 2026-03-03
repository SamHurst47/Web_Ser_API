import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from models import Users
from db import get_db

# --- 1. USER REGISTRATION ---

@patch("routers.users.get_password_hash")
def test_register_user_success(mock_hash, client):
    """Verifies successful registration and password hashing."""
    mock_hash.return_value = "hashed_password"
    
    # Mock DB session to simulate no existing user
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    def fake_refresh(obj):
        obj.id = 1
    mock_session.refresh.side_effect = fake_refresh
    
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    payload = {"email": "lewis.hamilton@mercedes.com", "password": "SuperSecretPassword123!"}
    resp = client.post("/api/v1/accounts/register", json=payload)
    
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["email"] == "lewis.hamilton@mercedes.com"
    assert resp.json()["id"] == 1

def test_register_user_duplicate_email(client):
    """Edge Case: Ensure 400 error when email is already in the database."""
    mock_session = MagicMock()
    # Simulate finding an existing user
    mock_session.query.return_value.filter.return_value.first.return_value = Users(id=1)
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    payload = {"email": "existing@f1.com", "password": "password123"}
    resp = client.post("/api/v1/accounts/register", json=payload)
    
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    # Match the actual message: "An account with this email already exists."
    assert "already exists" in resp.json()["detail"]


# --- 2. USER LOGIN ---

@patch("routers.users.verify_password")
def test_login_success(mock_verify, client):
    """Verifies login generates a JWT when credentials are valid."""
    mock_verify.return_value = True
    
    mock_session = MagicMock()
    fake_user = Users(id=1, email="driver@f1.com", hashed_password="hashed")
    mock_session.query.return_value.filter.return_value.first.return_value = fake_user
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    # OAuth2PasswordRequestForm uses data (form-encoded) not json
    form_data = {"username": "driver@f1.com", "password": "fastpassword"}
    resp = client.post("/api/v1/accounts/login", data=form_data)
    
    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"

@patch("routers.users.verify_password")
def test_login_invalid_password(mock_verify, client):
    """Edge Case: Ensure 401 error for incorrect credentials."""
    mock_verify.return_value = False # Password check fails
    
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = Users(id=1)
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    form_data = {"username": "driver@f1.com", "password": "wrong_password"}
    resp = client.post("/api/v1/accounts/login", data=form_data)
    
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# --- 3. ACCOUNT DELETION ---

def test_delete_user_account_success(client, authorized_header):
    """Verifies that an authorized user can delete their own account."""
    # This uses the conftest client which mocks get_current_user
    resp = client.delete("/api/v1/accounts", headers=authorized_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

def test_delete_user_account_unauthorized(unauthenticated_client):
    """Edge Case: Ensure account deletion is protected by JWT."""
    resp = unauthenticated_client.delete("/api/v1/accounts")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

