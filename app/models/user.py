from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.connection import Base

# Association table for User <-> Skill (many-to-many)
user_skills = Table(
    "user_skills",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    education_level = Column(String, nullable=True)
    degree_branch = Column(String, nullable=True)
    years_of_experience = Column(Float, default=0.0)
    preferred_domain = Column(String, nullable=True)
    preferred_job_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Many-to-many relationship to skills
    skills = relationship("Skill", secondary=user_skills, backref="users")

    # One-to-many relationships
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
