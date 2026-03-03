import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

# --- 1. LIST LAP SUMMARIES ---

def test_list_lap_summaries_success(client, authorized_header):
    """Verifies that a logged-in user can retrieve their saved laps."""
    resp = client.get("/api/v1/lap_summaries", headers=authorized_header)
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)

def test_list_lap_summaries_unauthorized(unauthenticated_client):
    """Edge Case: Ensure unauthorized requests are blocked."""
    resp = unauthenticated_client.get("/api/v1/lap_summaries")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# --- 2. IMPORT FROM OPENF1 ---

@patch("routers.lap_summary.requests.get")
def test_import_from_openf1_success(mock_requests_get, client, authorized_header):
    """Tests the full import pipeline with a mocked external API response."""
    # Configure fake OpenF1 response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "lap_number": 1,
            "lap_duration": 85.5,
            "st_speed": 320.0,
            "i1_speed": 290.0,
            "i2_speed": 300.0,
            "duration_sector_1": 25.1,
            "duration_sector_2": 35.2,
            "duration_sector_3": 25.2
        }
    ]
    mock_requests_get.return_value = mock_response
    
    # Use the 2023 Belgium example data identified in documentation
    params = "driver_number=1&session_key=9141"
    resp = client.post(f"/api/v1/lap_summaries/import_from_openf1?{params}", headers=authorized_header)
    
    assert resp.status_code == status.HTTP_202_ACCEPTED
    assert resp.json()["imported"] == 1
    assert resp.json()["session_key"] == 9141

@patch("routers.lap_summary.requests.get")
def test_import_from_openf1_external_fail(mock_requests_get, client, authorized_header):
    """Edge Case: Verify API handles external service (OpenF1) downtime (502)."""
    # 1. Force the mock to raise a connection error
    mock_requests_get.side_effect = Exception("OpenF1 Timeout")
    
    # 2. Prevent pytest from crashing on the exception
    client.raise_server_exceptions = False 
    
    # 3. Call the endpoint
    resp = client.post(
        "/api/v1/lap_summaries/import_from_openf1?driver_number=1&session_key=9141", 
        headers=authorized_header
    )
    
    # 4. Verify the API returned a 502 instead of crashing
    assert resp.status_code == status.HTTP_502_BAD_GATEWAY


# --- 3. UPDATE LAP SUMMARIES ---

@patch("routers.lap_summary.lap_service.update_lap_summaries")
def test_update_lap_summaries_success(mock_update, client, authorized_header):
    """Tests partial update (PUT) of lap metadata."""
    mock_update.return_value = [{
        "id": 1, 
        "owner_id": 1,
        "session_key": 9141,
        "driver_number": 1, 
        "lap_number": 1,
        "label": "Push Lap"
    }]

    payload = {"label": "Push Lap", "max_speed_kph": 335.0}
    resp = client.put("/api/v1/lap_summaries?driver_number=1&session_key=9141", json=payload, headers=authorized_header)
    
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()[0]["label"] == "Push Lap"

def test_update_lap_summaries_invalid_data(client, authorized_header):
    """Edge Case: Pydantic validation for negative speeds (422)."""
    payload = {"max_speed_kph": -50.0} # Schema 'ge=0' should catch this
    resp = client.put("/api/v1/lap_summaries?driver_number=1", json=payload, headers=authorized_header)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- 4. DELETE LAP SUMMARIES ---

@patch("routers.lap_summary.lap_service.delete_lap_summaries")
def test_delete_lap_summaries_success(mock_delete, client, authorized_header):
    """Verifies successful deletion returns 204 No Content."""
    mock_delete.return_value = 1
    resp = client.delete("/api/v1/lap_summaries?driver_number=1", headers=authorized_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

@patch("routers.lap_summary.lap_service.delete_lap_summaries")
def test_delete_lap_summaries_not_found(mock_delete, client, authorized_header):
    """Edge Case: Return 404 if no records match the deletion criteria."""
    mock_delete.return_value = 0
    resp = client.delete("/api/v1/lap_summaries?driver_number=99", headers=authorized_header)
    assert resp.status_code == status.HTTP_404_NOT_FOUND