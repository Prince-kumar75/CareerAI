from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, List, Optional
import logging

from app.models.user import User, user_skills
from app.models.skill import Skill
from app.models.career import Career, CareerSkill
from app.models.recommendation import Recommendation, Feedback

logger = logging.getLogger(__name__)

# --- Skill CRUD ---

def get_skill_by_name(db: Session, name: str) -> Optional[Skill]:
    return db.query(Skill).filter(Skill.name == name).first()

def get_or_create_skill(db: Session, name: str) -> Skill:
    name_clean = name.strip()
    skill = get_skill_by_name(db, name_clean)
    if not skill:
        skill = Skill(name=name_clean)
        db.add(skill)
        try:
            db.commit()
            db.refresh(skill)
        except IntegrityError:
            db.rollback()
            skill = get_skill_by_name(db, name_clean)
    return skill

# --- User CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: dict) -> User:
    # Extract skill names
    skills_list = user_data.pop("skills", [])
    
    # Create User instance
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Process and link skills
    db_skills = [get_or_create_skill(db, skill_name) for skill_name in skills_list]
    db_user.skills = db_skills
    db.commit()
    db.refresh(db_user)
    
    return db_user

# --- Career CRUD ---

def get_careers(db: Session) -> List[Career]:
    return db.query(Career).all()

def get_career(db: Session, career_id: int) -> Optional[Career]:
    return db.query(Career).filter(Career.id == career_id).first()

def get_career_by_title(db: Session, title: str) -> Optional[Career]:
    return db.query(Career).filter(Career.title == title).first()

# --- Recommendation & Feedback CRUD ---

def create_recommendation(db: Session, user_id: Optional[int], career_id: int, match_score: float) -> Recommendation:
    db_rec = Recommendation(user_id=user_id, career_id=career_id, match_score=match_score)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

def create_feedback(db: Session, user_id: Optional[int], career_id: int, rating: int, feedback_text: Optional[str]) -> Feedback:
    db_feedback = Feedback(user_id=user_id, career_id=career_id, rating=rating, feedback=feedback_text)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# --- Seeding Logic ---

DEFAULT_CAREERS = {
    "Data Scientist": {
        "description": "Analyzes and interprets complex data to help organizations make informed decisions using ML and statistics.",
        "domain": "Data Science",
        "skills": {
            "Python": 1.0, "SQL": 0.9, "Pandas": 0.9, "NumPy": 0.8, 
            "Scikit-learn": 0.9, "Statistics": 0.8, "Machine Learning": 0.9,
            "Tableau": 0.5, "Problem-solving": 0.7, "Communication": 0.7
        }
    },
    "Machine Learning Engineer": {
        "description": "Designs, builds, and deploys machine learning models and systems at scale.",
        "domain": "Machine Learning",
        "skills": {
            "Python": 1.0, "C++": 0.6, "TensorFlow": 0.9, "PyTorch": 0.9,
            "Scikit-learn": 0.8, "Docker": 0.7, "Kubernetes": 0.6, "Git": 0.7,
            "Deep Learning": 0.9, "MLOps": 0.8, "Problem-solving": 0.7
        }
    },
    "Frontend Developer": {
        "description": "Creates visually appealing and interactive user interfaces for web applications.",
        "domain": "Web Development",
        "skills": {
            "JavaScript": 1.0, "TypeScript": 0.8, "HTML": 0.9, "CSS": 0.9,
            "React": 0.9, "Angular": 0.6, "Vue": 0.5, "Figma": 0.7,
            "Git": 0.6, "TailwindCSS": 0.7, "Communication": 0.6
        }
    },
    "Backend Developer": {
        "description": "Designs, develops, and maintains server-side logic, databases, and APIs.",
        "domain": "Web Development",
        "skills": {
            "Java": 0.8, "Python": 0.8, "Go": 0.7, "Node.js": 0.7,
            "SQL": 0.9, "PostgreSQL": 0.8, "MongoDB": 0.7, "Redis": 0.6,
            "Docker": 0.7, "Git": 0.7, "APIs": 0.9, "Problem-solving": 0.8
        }
    },
    "DevOps Engineer": {
        "description": "Bridges development and operations to automate build, deployment, and infrastructure monitoring.",
        "domain": "DevOps",
        "skills": {
            "Docker": 0.9, "Kubernetes": 0.9, "Linux": 0.9, "Bash": 0.8,
            "Jenkins": 0.8, "CI/CD": 0.9, "AWS": 0.8, "Terraform": 0.9,
            "Ansible": 0.7, "Git": 0.8, "Automation": 0.8
        }
    },
    "Cloud Architect": {
        "description": "Designs and manages enterprise-grade cloud computing strategies and architectures.",
        "domain": "Cloud Computing",
        "skills": {
            "AWS": 0.9, "Azure": 0.7, "GCP": 0.6, "Terraform": 0.8,
            "Kubernetes": 0.7, "Docker": 0.7, "Networking": 0.8,
            "System Design": 0.9, "Cloud Security": 0.8, "Leadership": 0.7
        }
    },
    "Cyber Security Analyst": {
        "description": "Protects networks, systems, and data from security threats, hacks, and unauthorized access.",
        "domain": "Cyber Security",
        "skills": {
            "Linux": 0.8, "Cryptography": 0.7, "Network Security": 0.9,
            "Wireshark": 0.8, "Penetration Testing": 0.8, "IAM": 0.7,
            "Firewalls": 0.9, "SIEM": 0.7, "Threat Intelligence": 0.8, "Attention to Detail": 0.8
        }
    },
    "Database Administrator": {
        "description": "Maintains database servers, ensuring performance tuning, security, backups, and data availability.",
        "domain": "Database Administration",
        "skills": {
            "SQL": 1.0, "Oracle": 0.7, "MySQL": 0.8, "PostgreSQL": 0.9,
            "Database Tuning": 0.9, "Backup & Recovery": 0.9, "Data Warehousing": 0.7,
            "Attention to Detail": 0.8, "Problem-solving": 0.6
        }
    },
    "UI/UX Designer": {
        "description": "Designs human-centered user experiences and interactive interfaces using design thinking.",
        "domain": "Design",
        "skills": {
            "Figma": 1.0, "Sketch": 0.7, "Adobe XD": 0.8, "Wireframing": 0.9,
            "Prototyping": 0.9, "User Research": 0.8, "Visual Design": 0.8,
            "Creativity": 0.9, "Empathy": 0.8, "Communication": 0.8
        }
    },
    "Product Manager": {
        "description": "Guides the development, lifecycle, strategy, and business vision of a software product.",
        "domain": "Product Management",
        "skills": {
            "Product Strategy": 1.0, "Agile": 0.9, "Scrum": 0.8, "Roadmapping": 0.9,
            "Market Research": 0.7, "Jira": 0.8, "Leadership": 0.9, "Communication": 0.9,
            "Time Management": 0.8, "Conflict Resolution": 0.7
        }
    },
    "Data Analyst": {
        "description": "Collects, processes, and performs statistical analyses on data to create reports and visualizations.",
        "domain": "Business Intelligence",
        "skills": {
            "SQL": 0.9, "Excel": 0.8, "Tableau": 0.8, "PowerBI": 0.8,
            "Python": 0.6, "Data Visualization": 0.9, "Statistics": 0.7,
            "Communication": 0.8, "Reporting": 0.8, "Analytical Thinking": 0.8
        }
    }
}

def seed_database(db: Session):
    """
    Seeds default career roles and required skills mapping to the database.
    """
    logger.info("Starting database seeding...")
    
    # 1. Add careers and mapping
    for title, info in DEFAULT_CAREERS.items():
        career = get_career_by_title(db, title)
        if not career:
            logger.info(f"Creating career: {title}")
            career = Career(
                title=title,
                description=info["description"],
                domain=info["domain"]
            )
            db.add(career)
            db.commit()
            db.refresh(career)
            
        # Process required skills
        for skill_name, importance in info["skills"].items():
            skill = get_or_create_skill(db, skill_name)
            
            # Check if mapping already exists
            mapping = db.query(CareerSkill).filter(
                CareerSkill.career_id == career.id,
                CareerSkill.skill_id == skill.id
            ).first()
            
            if not mapping:
                logger.info(f"Linking skill {skill_name} to career {title} with importance {importance}")
                mapping = CareerSkill(
                    career_id=career.id,
                    skill_id=skill.id,
                    importance=importance
                )
                db.add(mapping)
                
        db.commit()
        
    logger.info("Database seeding complete!")
