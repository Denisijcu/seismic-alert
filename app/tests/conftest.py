import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.core.db import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_llm_agents(monkeypatch):
    """Evita llamadas reales al NIM en los tests."""
    def fake_classify_event(event, prompt):
        return json.dumps({"category": "seismic_event", "severity": event.get("magnitude", 0)})

    def fake_validate_event(payload, prompt):
        return json.dumps({"should_alert": False, "confidence": 0.9, "reason": "mocked"})

    def fake_redact_message(payload, prompt):
        return "Mensaje de alerta simulado"

    def fake_dispatch_alert(message, channels):
        return {"sent": True, "channels": channels}

    monkeypatch.setattr("app.orchestration.router.classify_event", fake_classify_event)
    monkeypatch.setattr("app.orchestration.router.validate_event", fake_validate_event)
    monkeypatch.setattr("app.orchestration.router.redact_message", fake_redact_message)
    monkeypatch.setattr("app.orchestration.router.dispatch_alert", fake_dispatch_alert)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()