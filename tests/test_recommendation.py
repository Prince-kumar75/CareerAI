import pytest
import pandas as pd
from app.ml.preprocess import clean_dataframe, build_preprocessor_pipeline
from app.ml.predict import predict_careers
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import RecommendationRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database.crud import seed_database, get_careers

@pytest.fixture
def sample_profile_df():
    data = {
        "education_level": ["Bachelor's", None],
        "degree_branch": ["Computer Science", "Information Technology"],
        "years_of_experience": [3, "2"],
        "technical_skills": ["Python, SQL, React", "Java, Docker"],
        "programming_languages": ["Python, JavaScript", "Java"],
        "soft_skills": ["Problem-solving, Communication", "Teamwork"],
        "interests": ["Machine Learning, UI/UX", "Backend Development"],
        "preferred_domain": ["Data Science", "Web Development"],
        "preferred_job_type": ["Full-time", "Remote"],
        "career_interests": ["AI & Big Data", "Cloud"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_db_session():
    # SQLite memory database for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    seed_database(db)
    try:
        yield db
    finally:
        db.close()

def test_clean_dataframe(sample_profile_df):
    df_clean = clean_dataframe(sample_profile_df)
    
    # Check that missing/null values are handled
    assert df_clean["education_level"].iloc[1] == "Missing"
    # Check numerical columns are cast correctly
    assert df_clean["years_of_experience"].dtype == float
    assert df_clean["years_of_experience"].iloc[0] == 3.0
    assert df_clean["years_of_experience"].iloc[1] == 2.0
    
    # Check string stripping
    assert df_clean["technical_skills"].iloc[0] == "Python, SQL, React"

def test_preprocessor_pipeline_shape(sample_profile_df):
    df_clean = clean_dataframe(sample_profile_df)
    pipeline = build_preprocessor_pipeline()
    
    # Fit & Transform
    pipeline.fit(df_clean)
    features = pipeline.transform(df_clean)
    
    # Verify shape (features must be 2D array)
    assert len(features.shape) == 2
    assert features.shape[0] == 2

def test_recommendation_logic_empty_skills(mock_db_session):
    request = RecommendationRequest(
        education_level="Bachelor's",
        degree_branch="Computer Science",
        technical_skills=[],
        programming_languages=[],
        soft_skills=[],
        interests=[],
        years_of_experience=0,
        preferred_domain="Web Development",
        preferred_job_type="Full-time",
        career_interests=[]
    )
    
    response = RecommendationService.generate_recommendations(mock_db_session, request)
    
    # Verify output format
    assert len(response.recommendations) > 0
    first_rec = response.recommendations[0]
    
    # Under empty skills, existing_skills must be empty
    assert len(first_rec.existing_skills) == 0
    # Must have missing skills list
    assert len(first_rec.missing_skills) > 0
    # Must have fallback explanation
    assert "career matches" in first_rec.reason.lower()

def test_recommendation_logic_populated_skills(mock_db_session):
    request = RecommendationRequest(
        education_level="Bachelor's",
        degree_branch="Computer Science",
        technical_skills=["Python", "Pandas", "Scikit-learn"],
        programming_languages=["Python", "SQL"],
        soft_skills=["Problem-solving", "Communication"],
        interests=["Data Analysis", "Machine Learning"],
        years_of_experience=3.0,
        preferred_domain="Data Science",
        preferred_job_type="Full-time",
        career_interests=["AI & Big Data"]
    )
    
    response = RecommendationService.generate_recommendations(mock_db_session, request)
    
    # Verify recommendations exist
    assert len(response.recommendations) == 5
    
    # Find Data Scientist recommendation (if any)
    ds_rec = next((r for r in response.recommendations if r.career == "Data Scientist"), None)
    
    if ds_rec:
        # Check intersection mapping
        assert "Python" in ds_rec.existing_skills
        assert "SQL" in ds_rec.existing_skills
        # Check missing skills mapping
        assert "Statistics" in ds_rec.missing_skills or "Tableau" in ds_rec.missing_skills
        # Check dynamic reasoning
        assert "recommended because your skills" in ds_rec.reason.lower()
