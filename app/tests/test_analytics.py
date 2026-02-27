from unittest.mock import patch, MagicMock
from schemas.analytics import PaceTrendResponse, IdealLapsResponse

# --- 1. Test Pace Trend ---
@patch("routers.analytics.analytics_service.get_pace_trend")
def test_get_pace_trend(mock_get_trend, client):
    # Create a fake database row with the exact attributes the router expects
    mock_lap = MagicMock()
    mock_lap.driver_number = 1
    mock_lap.session_name = "Race"
    mock_lap.lap_number = 1
    mock_lap.lap_duration = 85.500
    
    mock_get_trend.return_value = [mock_lap]

    resp = client.get("/api/v1/analytics/pace-trend?year=2024&location=Monza")
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["year"] == 2024
    assert data["location"] == "Monza"
    assert len(data["trends"]) == 1
    assert data["trends"][0]["driver_number"] == 1
    assert data["trends"][0]["laps"][0]["lap_duration"] == 85.500


# --- 2. Test Ideal Laps ---
@patch("routers.analytics.analytics_service.get_overall_ideal_laps")
@patch("routers.analytics.analytics_service.get_ideal_laps_grouped")
def test_get_ideal_laps(mock_get_grouped, mock_get_overall, client):
    # Fake the "Franken-lap" (Overall best)
    mock_overall = MagicMock()
    mock_overall.session_name = "Race"
    mock_overall.best_s1 = 25.000
    mock_overall.best_s2 = 30.000
    mock_overall.best_s3 = 20.000
    mock_get_overall.return_value = [mock_overall]

    # Fake a specific driver's ideal lap
    mock_driver = MagicMock()
    mock_driver.driver_number = 4  # Lando!
    mock_driver.session_name = "Race"
    mock_driver.best_s1 = 25.100
    mock_driver.best_s2 = 30.200
    mock_driver.best_s3 = 20.100
    mock_driver.actual_best = 75.800
    mock_get_grouped.return_value = [mock_driver]

    resp = client.get("/api/v1/analytics/ideal-laps?year=2024&location=Monza")
    
    assert resp.status_code == 200
    data = resp.json()
    
    # Verify Overall
    assert data["overall_ideal_laps"][0]["ideal_lap_time"] == 75.000  # 25 + 30 + 20
    
    # Verify Driver
    assert data["driver_ideal_laps"][0]["driver_number"] == 4
    assert data["driver_ideal_laps"][0]["ideal_lap_time"] == 75.400  # 25.1 + 30.2 + 20.1
    assert data["driver_ideal_laps"][0]["potential_improvement"] == 0.400  # 75.8 - 75.4


# --- 3. Test True Pace ---
@patch("routers.analytics.analytics_service.get_true_pace_grouped")
def test_get_true_pace(mock_get_true_pace, client):
    # Fake the mathematical average returned by the DB
    mock_pace = MagicMock()
    mock_pace.driver_number = 1
    mock_pace.session_name = "Race"
    mock_pace.avg_pace = 86.250
    mock_pace.lap_count = 52
    
    mock_get_true_pace.return_value = [mock_pace]

    resp = client.get("/api/v1/analytics/true-pace?year=2024&location=Monza")
    
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["driver_number"] == 1
    assert data[0]["true_average_pace"] == 86.250
    assert data[0]["valid_laps_counted"] == 52