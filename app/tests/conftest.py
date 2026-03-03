import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Force Python to look inside the 'app' folder
current_dir = os.path.dirname(__file__)
app_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, app_dir)

from main import app  
from db import get_db
from models import LapSummary, Users
from services.dependencies import get_current_user 

@pytest.fixture
def client():
    """
    Standard client with security and DB bypassed.
    This is what your existing tests expect.
    """
    def mock_get_db():
        mock_session = MagicMock()
        return mock_session
        
    def mock_get_current_user():
        return Users(id=1, email="test_user@f1.com", hashed_password="fakehash")
        
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def authorized_header():
    """
    This provides the fixture your analytics tests are looking for.
    Since get_current_user is mocked above, the content of this 
    header doesn't technically matter, but it must exist for the test to run.
    """
    return {"Authorization": "Bearer fake_token_for_testing"}

@pytest.fixture
def unauthenticated_client():
    """
    A special client that DOES NOT override the security lock.
    Use this to test if 401 Unauthorized errors work correctly.
    """
    def mock_get_db():
        return MagicMock()

    # We only override the DB, NOT the get_current_user lock
    app.dependency_overrides[get_db] = mock_get_db
    
    yield TestClient(app)
    app.dependency_overrides.clear()