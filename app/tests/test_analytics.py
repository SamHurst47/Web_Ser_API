import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

# --- 1. PACE TREND ENDPOINT ---

@patch("routers.analytics.analytics_service.get_pace_trend")
def test_get_pace_trend_success(mock_get_trend, client, authorized_header):
    """
    Edge Case: Verify rounding and complex data mapping.
    Ensures that multiple laps for a single driver are grouped correctly.
    """
    mock_lap1 = MagicMock(driver_number=1, session_name="Race", lap_number=1, lap_duration=85.5555)
    mock_lap2 = MagicMock(driver_number=1, session_name="Race", lap_number=2, lap_duration=84.1111)
    mock_get_trend.return_value = [mock_lap1, mock_lap2]

    resp = client.get(
        "/api/v1/analytics/pace-trend?year=2024&location=Monza",
        headers=authorized_header
    )
    
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    # Verify the grouping logic in the router
    assert len(data["trends"]) == 1
    assert len(data["trends"][0]["laps"]) == 2
    # Logic check: Verify data remains precise
    assert data["trends"][0]["laps"][0]["lap_duration"] == 85.5555

def test_get_pace_trend_unauthorized(unauthenticated_client):
    """
    Edge Case: Security Layer.
    Uses the client that hasn't bypassed the security lock.
    """
    # Use the client that actually enforces the JWT check
    resp = unauthenticated_client.get("/api/v1/analytics/pace-trend?year=2024&location=Monza")
    assert resp.status_code == 401 # This will now correctly return 401

def test_get_pace_trend_invalid_params(client, authorized_header):
    """
    Edge Case: Input Validation.
    Testing strings in integer fields to trigger Pydantic validation.
    """
    resp = client.get(
        "/api/v1/analytics/pace-trend?year=invalid_year&location=Monza", 
        headers=authorized_header
    )
    # Update from HTTP_422_UNPROCESSABLE_ENTITY to HTTP_422_UNPROCESSABLE_CONTENT
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- 2. IDEAL LAPS ENDPOINT ---

@patch("routers.analytics.analytics_service.get_overall_ideal_laps")
@patch("routers.analytics.analytics_service.get_ideal_laps_grouped")
def test_get_ideal_laps_math_integrity(mock_get_grouped, mock_get_overall, client, authorized_header):
    """
    Edge Case: Mathematical Precision.
    Checks if the router correctly handles 'None' values from the DB (e.g., if a driver crashed in S1).
    """
    # Mock Overall: S1 is missing (None)
    mock_overall = MagicMock(session_name="Qualifying", best_s1=None, best_s2=30.0, best_s3=20.0)
    mock_get_overall.return_value = [mock_overall]
    
    # Mock Driver: Perfect sector times
    mock_driver = MagicMock(
        driver_number=44, session_name="Qualifying", 
        best_s1=28.123, best_s2=35.456, best_s3=22.890, actual_best=86.750
    )
    mock_get_grouped.return_value = [mock_driver]

    resp = client.get(
        "/api/v1/analytics/ideal-laps?year=2024&location=Monza",
        headers=authorized_header
    )
    
    data = resp.json()
    # The router should skip the overall lap because S1 is None (based on the 'if row.best_s1...' logic)
    assert len(data["overall_ideal_laps"]) == 0
    # The driver lap should calculate correctly
    assert data["driver_ideal_laps"][0]["ideal_lap_time"] == round(28.123 + 35.456 + 22.890, 3)

def test_get_ideal_laps_not_found(client, authorized_header):
    """
    Edge Case: Empty Database.
    Ensures the API doesn't crash if the user requests a year with no data.
    """
    with patch("routers.analytics.analytics_service.get_overall_ideal_laps", return_value=[]):
        with patch("routers.analytics.analytics_service.get_ideal_laps_grouped", return_value=[]):
            resp = client.get(
                "/api/v1/analytics/ideal-laps?year=1950&location=Silverstone",
                headers=authorized_header
            )
            assert resp.status_code == 200
            assert resp.json()["overall_ideal_laps"] == []


# --- 3. TRUE PACE ENDPOINT ---

@patch("routers.analytics.analytics_service.get_true_pace_grouped")
def test_get_true_pace_outlier_filtering(mock_get_true_pace, client, authorized_header):
    """
    Edge Case: Data Filtering.
    Ensures the router suppresses drivers who have no valid average pace (e.g., DNF on lap 1).
    """
    # Driver 1: Valid pace
    # Driver 2: None pace (DNF)
    mock_results = [
        MagicMock(driver_number=1, session_name="Race", avg_pace=109.500, lap_count=44),
        MagicMock(driver_number=2, session_name="Race", avg_pace=None, lap_count=0)
    ]
    mock_get_true_pace.return_value = mock_results

    resp = client.get(
        "/api/v1/analytics/true-pace?year=2023&location=Belgium",
        headers=authorized_header
    )
    
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_number"] == 1
    assert "avg_pace" not in data[0] # Verify Pydantic alias mapping



