"""
Test configuration and fixtures for pytest.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.core.models import Lead, Conversation, Message

# Test database URL (SQLite in-memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_lead(db):
    """Create a sample lead for testing."""
    lead = Lead(
        session_id="test-session-123",
        name="Juan Pérez",
        email="juan@example.com",
        phone="+34666777888",
        project_type="APARTMENT_REFORM",
        budget=25000.0,
        timeline="3 meses",
        timeline_months=3,
        location="Vigo",
        score=65,
        category="WARM"
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@pytest.fixture
def sample_conversation(db, sample_lead):
    """Create a sample conversation for testing."""
    conversation = Conversation(
        session_id="test-session-123",
        lead_id=sample_lead.id,
        channel="web",
        language="es"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
