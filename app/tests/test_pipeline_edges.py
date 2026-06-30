import pytest


@pytest.mark.parametrize(
    "magnitude, expected_status",
    [
        (0.1, "discarded"),
        (4.2, "discarded"),
        (5.1, "monitor"),
        (7.0, "pending_human_review"),
    ],
)

def test_ingest_event_thresholds(client, magnitude, expected_status):
    payload = {
        "event_id": f"test-{magnitude}",
        "magnitude": magnitude,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }

    response = client.post("/ingest/event", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "db_id" in data
    assert "result" in data
    assert data["result"]["status"] == expected_status


def test_feedback_missing_note(client):
    payload = {
        "event_id": "test-001",
        "was_correct": True,
    }

    response = client.post("/feedback", json=payload)
    assert response.status_code in (200, 422)

def test_hitl_approve_flow(client):
    payload = {
        "event_id": "test-hitl-001",
        "magnitude": 7.0,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }
    response = client.post("/ingest/event", json=payload)
    assert response.status_code == 200
    assert response.json()["result"]["status"] == "pending_human_review"

    approve_response = client.post(f"/events/{payload['event_id']}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "alert_sent"


def test_hitl_reject_flow(client):
    payload = {
        "event_id": "test-hitl-002",
        "magnitude": 7.0,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }
    response = client.post("/ingest/event", json=payload)
    assert response.status_code == 200

    reject_response = client.post(f"/events/{payload['event_id']}/reject")
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"


def test_hitl_double_approve_fails(client):
    payload = {
        "event_id": "test-hitl-003",
        "magnitude": 7.0,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }
    client.post("/ingest/event", json=payload)
    client.post(f"/events/{payload['event_id']}/approve")

    second_attempt = client.post(f"/events/{payload['event_id']}/approve")
    assert second_attempt.status_code == 409

def test_pending_events_endpoint(client):
    payload = {
        "event_id": "test-pending-001",
        "magnitude": 7.0,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }
    client.post("/ingest/event", json=payload)

    response = client.get("/events/pending")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert any(e["event_id"] == "test-pending-001" for e in data["events"])