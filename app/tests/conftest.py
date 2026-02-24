import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# 1. Force Python to look directly inside the 'app' folder
current_dir = os.path.dirname(__file__)
app_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, app_dir)

# 2. Import your REAL app and the dependency
from main import app  # <-- Import your actual FastAPI app here!
from db import get_db
from models import LapSummary

@pytest.fixture
def client():
    def mock_get_db():
        mock_session = MagicMock()
        
        # Create dummy data
        dummy_lap = LapSummary(
            id=1, session_key=1234, year=2025, location="Melbourne",
            session_name="AUS-RACE", driver_number=1, lap_number=1,
            lap_duration=85.5, max_speed_kph=330.5, avg_speed_kph=245.0, label="Clean"
        )
        
        # Configure the mock
        mock_query = MagicMock()
        mock_query.all.return_value = [dummy_lap]
        mock_session.query.return_value = mock_query
        return mock_session
        
    # Override the dependency on your REAL app
    app.dependency_overrides[get_db] = mock_get_db
    
    yield TestClient(app)
    
    # Clean up the override after the test finishes
    app.dependency_overrides.clear()