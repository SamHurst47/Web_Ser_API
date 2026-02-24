from unittest.mock import patch

# 1. Test the GET endpoint (Lists summaries)
def test_list_lap_summaries(client):
    resp = client.get("/api/v1/lap_summaries")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# 2. Test the POST endpoint (Imports from OpenF1)
# We patch 'requests.get' so we don't actually hit the real internet during the test
@patch("routers.lap_summary.requests.get")
def test_import_from_openf1(mock_requests_get, client):
    # Configure our fake OpenF1 API response
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = [
        {
            "lap_number": 1,
            "lap_duration": 85.5,
            "st_speed": 320.0,
            "i1_speed": 290.0,
            "i2_speed": 300.0
        }
    ]
    
    # Call the endpoint with required query parameters
    resp = client.post("/api/v1/lap_summaries/import_from_openf1?driver_number=1&session_key=1234")
    
    assert resp.status_code == 202
    assert resp.json()["imported"] == 1
    assert resp.json()["session_key"] == 1234

# 3. Test the PUT endpoint (Updates a summary)
# We patch the lap_service so we don't have to build a highly complex mock database
@patch("routers.lap_summary.lap_service.update_lap_summaries")
def test_update_lap_summaries(mock_update, client):
    # Tell the mock service to return a dummy list so the router doesn't throw a 404
    mock_update.return_value = [{"id": 1, "driver_number": 1, "lap_number": 1}]
    
    # A dummy payload representing LapSummaryUpdate
    payload = {"label": "Push Lap"} 
    
    resp = client.put("/api/v1/lap_summaries?driver_number=1", json=payload)
    assert resp.status_code == 200

# 4. Test the DELETE endpoint (Deletes a summary)
@patch("routers.lap_summary.lap_service.delete_lap_summaries")
def test_delete_lap_summaries(mock_delete, client):
    # Tell the mock service that it successfully deleted 1 record
    mock_delete.return_value = 1
    
    resp = client.delete("/api/v1/lap_summaries?driver_number=1")
    
    # 204 No Content means a successful deletion!
    assert resp.status_code == 204