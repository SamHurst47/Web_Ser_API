from unittest.mock import patch, MagicMock
from db import get_db
from models import Users

# 1. Test Registration
@patch("routers.users.get_password_hash")
def test_register_user(mock_hash, client):
    mock_hash.return_value = "super_secure_hashed_password"
    
    mock_session = MagicMock()
    # Explicitly tell it to return None (meaning "No user exists with this email yet")
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    def fake_refresh(obj):
        obj.id = 1
    mock_session.refresh.side_effect = fake_refresh
    
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    payload = {"email": "new_driver@f1.com", "password": "fastpassword"}
    resp = client.post("/api/v1/accounts/register", json=payload)
    
    assert resp.status_code == 201
    assert resp.json()["email"] == "new_driver@f1.com"
    assert resp.json()["id"] == 1 # Now it successfully has an ID!


# 2. Test Login
@patch("routers.users.verify_password")
def test_login_user(mock_verify, client):
    mock_verify.return_value = True
    
    # Create ONE specific mock session for this test
    mock_session = MagicMock()
    # Explicitly tell it to return a fake user (meaning "Login successful!")
    fake_user = Users(id=1, email="new_driver@f1.com", hashed_password="hashed")
    mock_session.query.return_value.filter.return_value.first.return_value = fake_user
    
    # Force FastAPI to use THIS exact mock session
    client.app.dependency_overrides[get_db] = lambda: mock_session
    
    form_data = {"username": "new_driver@f1.com", "password": "fastpassword"}
    resp = client.post("/api/v1/accounts/login", data=form_data)
    
    assert resp.status_code == 200
    assert "access_token" in resp.json()

# 3. Test Account Deletion
def test_delete_user_account(client):
    # The default overrides from conftest.py work perfectly for this one
    resp = client.delete("/api/v1/accounts")
    assert resp.status_code == 204