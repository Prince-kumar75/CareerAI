import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.connection import Base, get_db
from app.database.crud import seed_database

# Explicitly import models to register them on Base.metadata
from app.models.user import User, user_skills
from app.models.career import Career, CareerSkill
from app.models.skill import Skill
from app.models.recommendation import Recommendation, Feedback

# Use a temporary SQLite file database for integration tests to ensure
# multiple connections (from the FastAPI client and test runner) see the same tables.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    # Clean up any leftover test database
    if os.path.exists("./test_temp.db"):
        try:
            os.remove("./test_temp.db")
        except Exception:
            pass
            
    # Set up the DB schema
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)  # Seed default careers
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        
        # Clean up the test database file
        if os.path.exists("./test_temp.db"):
            try:
                os.remove("./test_temp.db")
            except Exception:
                pass

@pytest.fixture(name="client")
def client_fixture(session):
    # Override get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Career Recommendation" in response.text

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"

def test_get_careers_list(client):
    response = client.get("/api/v1/careers")
    assert response.status_code == 200
    careers = response.json()
    assert len(careers) > 0
    # Match the titles in seed database
    assert any(c["title"] == "Data Scientist" for c in careers)
    assert any(c["title"] == "Frontend Developer" for c in careers)

def test_get_career_by_id(client):
    # First query all careers to get a valid ID
    list_resp = client.get("/api/v1/careers")
    assert list_resp.status_code == 200
    careers = list_resp.json()
    career_id = careers[0]["id"]
    
    # Query specific career details
    response = client.get(f"/api/v1/careers/{career_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == career_id
    assert "title" in data
    assert "career_skills" in data

def test_get_career_by_invalid_id(client):
    response = client.get("/api/v1/careers/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_and_get_user(client):
    user_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "education_level": "Master's",
        "degree_branch": "Data Science",
        "years_of_experience": 2.5,
        "preferred_domain": "Data Science",
        "preferred_job_type": "Remote",
        "skills": ["Python", "SQL", "Pandas"]
    }
    
    # Create User
    create_resp = client.post("/api/v1/users/", json=user_payload)
    assert create_resp.status_code == 201
    user_data = create_resp.json()
    assert user_data["id"] is not None
    assert user_data["email"] == "jane@example.com"
    assert len(user_data["skills"]) == 3
    
    # Retrieve User by ID
    get_resp = client.get(f"/api/v1/users/{user_data['id']}")
    assert get_resp.status_code == 200
    retrieved_data = get_resp.json()
    assert retrieved_data["name"] == "Jane Doe"
    assert retrieved_data["email"] == "jane@example.com"

def test_create_duplicate_user(client):
    user_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "skills": ["Python"]
    }
    
    # Create once
    resp1 = client.post("/api/v1/users/", json=user_payload)
    assert resp1.status_code == 201
    
    # Create twice
    resp2 = client.post("/api/v1/users/", json=user_payload)
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["detail"].lower()

def test_recommendation_endpoint(client):
    profile_payload = {
        "education_level": "Bachelor's",
        "degree_branch": "Computer Science",
        "technical_skills": ["Python", "SQL", "Scikit-learn"],
        "programming_languages": ["Python", "SQL"],
        "soft_skills": ["Problem-solving"],
        "interests": ["Machine Learning"],
        "years_of_experience": 1.5,
        "preferred_domain": "Data Science",
        "preferred_job_type": "Full-time",
        "career_interests": ["AI & Big Data"]
    }
    
    response = client.post("/api/v1/recommend", json=profile_payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) == 5
    assert recs[0]["career"] is not None
    assert recs[0]["match_score"] > 0
    assert "existing_skills" in recs[0]
    assert "missing_skills" in recs[0]
    assert "reason" in recs[0]
    assert "suggested_learning_areas" in recs[0]

def test_recommendation_invalid_input(client):
    # Missing education_level and other required fields
    profile_payload = {
        "education_level": "Bachelor's",
        "degree_branch": "Computer Science"
        # missing remaining fields
    }
    response = client.post("/api/v1/recommend", json=profile_payload)
    assert response.status_code == 422  # validation error

def test_feedback_endpoint(client):
    feedback_payload = {
        "career_title": "Data Scientist",
        "rating": 5,
        "feedback": "Perfect recommendation!"
    }
    
    response = client.post("/api/v1/feedback/", json=feedback_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["rating"] == 5
    assert data["feedback"] == "Perfect recommendation!"
