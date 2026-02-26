import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# 1. Force Python to look directly inside the 'app' folder
current_dir = os.path.dirname(__file__)
app_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, app_dir)

from main import app  
from db import get_db
from models import LapSummary, Users
from services.dependencies import get_current_user # Import your lock

@pytest.fixture
def client():
    def mock_get_db():
        mock_session = MagicMock()
        dummy_lap = LapSummary(
            id=1, owner_id=1, session_key=1234, year=2025, location="Melbourne",
            session_name="AUS-RACE", driver_number=1, lap_number=1,
            lap_duration=85.5, max_speed_kph=330.5, label="Clean"
        )
        mock_query = MagicMock()
        mock_query.all.return_value = [dummy_lap]
        mock_session.query.return_value = mock_query
        return mock_session
        
    def mock_get_current_user():
        # Return a fake user with an ID of 1 so the router doesn't crash
        return Users(id=1, email="test_user@f1.com", hashed_password="fakehash")
        
    # Override BOTH the database and the security lock
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()