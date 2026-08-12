from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.career import SkillResponse

class UserBase(BaseModel):
    name: str
    email: EmailStr
    education_level: Optional[str] = "Bachelor's"
    degree_branch: Optional[str] = "Computer Science"
    years_of_experience: float = Field(default=0.0, ge=0.0)
    preferred_domain: Optional[str] = "Web Development"
    preferred_job_type: Optional[str] = "Full-time"

class UserCreate(UserBase):
    skills: List[str] = Field(default=[], description="List of technical/soft skills")

class UserResponse(UserBase):
    id: int
    created_at: datetime
    skills: List[SkillResponse] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    # Custom validator/getter helper for lists if needed
    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Allow standard model validation from ORM
        return super().model_validate(obj, **kwargs)
