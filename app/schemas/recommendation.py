from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecommendationRequest(BaseModel):
    education_level: str = Field(..., example="Bachelor's")
    degree_branch: str = Field(..., example="Computer Science")
    technical_skills: List[str] = Field(..., example=["Python", "Pandas", "Scikit-learn"])
    programming_languages: List[str] = Field(..., example=["Python", "SQL"])
    soft_skills: List[str] = Field(..., example=["Problem-solving", "Communication"])
    interests: List[str] = Field(..., example=["Data Analysis", "Machine Learning"])
    years_of_experience: float = Field(..., ge=0, example=2.0)
    preferred_domain: str = Field(..., example="Data Science")
    preferred_job_type: str = Field(..., example="Full-time")
    career_interests: List[str] = Field(..., example=["AI & Big Data"])
    
    # Optional field to associate recommendation with a specific user in the database
    user_id: Optional[int] = Field(None, example=1)

class RecommendationDetail(BaseModel):
    career: str = Field(..., example="Data Scientist")
    match_score: float = Field(..., example=91.5)
    existing_skills: List[str] = Field(..., example=["Python", "Pandas", "Scikit-learn"])
    missing_skills: List[str] = Field(..., example=["SQL", "Deep Learning"])
    reason: str = Field(..., example="Strong Python and machine learning skills match the requirements of a Data Scientist role.")
    suggested_learning_areas: List[str] = Field(..., example=["Learn advanced SQL queries", "Deepen knowledge in Neural Networks and PyTorch"])

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationDetail]

class FeedbackRequest(BaseModel):
    user_id: Optional[int] = Field(None, example=1)
    career_title: str = Field(..., example="Data Scientist")  # Match on title to make it easy for API clients
    rating: int = Field(..., ge=1, le=5, example=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, example="Highly accurate recommendation.")

class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int]
    career_id: int
    rating: int
    feedback: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
