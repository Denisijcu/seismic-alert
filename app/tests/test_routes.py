def test_ingest_event(client):
    payload = {
        "event_id": "test-001",
        "magnitude": 4.2,
        "depth_km": 10.5,
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp_utc": "2026-06-29T18:08:51Z",
    }

    response = client.post("/ingest/event", json=payload)
    assert response.status_code == 200
    assert "db_id" in response.json()


def test_feedback(client):
    payload = {
        "event_id": "test-001",
        "was_correct": True,
        "note": "Test ok",
    }

    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["stored"] is True