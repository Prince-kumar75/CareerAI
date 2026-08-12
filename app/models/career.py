from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class CareerSkill(Base):
    __tablename__ = "career_skills"

    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    importance = Column(Float, default=1.0)  # Skill importance weight

    # Relationships
    career = relationship("Career", back_populates="career_skills")
    skill = relationship("Skill", backref="career_skills_association")

class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    domain = Column(String, nullable=False)

    # Relationship to skills via the association object
    career_skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    
    # One-to-many relationship
    recommendations = relationship("Recommendation", back_populates="career", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="career", cascade="all, delete-orphan")
