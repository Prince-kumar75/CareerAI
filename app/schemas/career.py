from pydantic import BaseModel
from typing import List

class SkillBase(BaseModel):
    name: str

class SkillResponse(SkillBase):
    id: int
    
    class Config:
        from_attributes = True

class CareerSkillResponse(BaseModel):
    skill: SkillResponse
    importance: float
    
    class Config:
        from_attributes = True

class CareerBase(BaseModel):
    title: str
    description: str
    domain: str

class CareerResponse(CareerBase):
    id: int
    
    class Config:
        from_attributes = True

class CareerDetailResponse(CareerResponse):
    career_skills: List[CareerSkillResponse] = []
    
    class Config:
        from_attributes = True
