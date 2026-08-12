from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.schemas.recommendation import RecommendationRequest, RecommendationDetail, RecommendationResponse
from app.ml.predict import predict_careers
from app.models.career import Career
from app.database.crud import get_career_by_title, create_recommendation, get_user

class RecommendationService:
    @staticmethod
    def generate_recommendations(
        db: Session, 
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Takes user profile inputs, runs ML predictions, calculates skill gaps, 
        generates personalized explanations and learning paths, and saves 
        recommendation records to the DB.
        """
        # 1. Format the request data into the shape expected by the preprocessor
        profile_dict = {
            "education_level": request.education_level,
            "degree_branch": request.degree_branch,
            "years_of_experience": request.years_of_experience,
            "technical_skills": ", ".join(request.technical_skills),
            "programming_languages": ", ".join(request.programming_languages),
            "soft_skills": ", ".join(request.soft_skills),
            "interests": ", ".join(request.interests),
            "preferred_domain": request.preferred_domain,
            "preferred_job_type": request.preferred_job_type,
            "career_interests": ", ".join(request.career_interests)
        }

        # 2. Get top 5 predicted career roles and their match probabilities from ML model
        # Try to run predictions. If model is not trained yet, it will throw FileNotFoundError.
        try:
            predictions = predict_careers(profile_dict, top_n=5)
        except FileNotFoundError:
            # Fallback for testing/dev if model is not trained yet
            # In an actual deployment, the model should be pretrained.
            # We'll return a static prediction for testing if the file doesn't exist.
            predictions = [
                ("Data Scientist", 90.0),
                ("Machine Learning Engineer", 85.0),
                ("Data Analyst", 75.0),
                ("Backend Developer", 60.0),
                ("Product Manager", 50.0)
            ]

        # 3. Standardize user skills for comparison
        user_skills_set = {
            s.strip().lower() 
            for s in (request.technical_skills + request.programming_languages + request.soft_skills)
            if s.strip()
        }

        recommended_details = []

        # 4. Perform skill gap analysis and reasoning for each predicted career
        for career_title, score in predictions:
            # Query career and its required skills from the DB
            db_career = get_career_by_title(db, career_title)
            
            if db_career:
                career_id = db_career.id
                description = db_career.description
                domain = db_career.domain
                
                # Fetch required skills from db association
                career_skills_map = {
                    cs.skill.name: cs.importance 
                    for cs in db_career.career_skills
                }
            else:
                # Fallback if DB isn't seeded (though it will be on startup)
                career_id = None
                description = "Specialized role in software/data systems."
                domain = "Technology"
                career_skills_map = {}

            # Perform case-insensitive intersection and difference
            existing_skills = []
            missing_skills_with_importance = []

            for req_skill, importance in career_skills_map.items():
                if req_skill.lower() in user_skills_set:
                    existing_skills.append(req_skill)
                else:
                    missing_skills_with_importance.append((req_skill, importance))

            # Sort missing skills by importance descending so the most critical are shown first
            missing_skills_with_importance.sort(key=lambda x: x[1], reverse=True)
            missing_skills = [skill for skill, _ in missing_skills_with_importance]

            # 5. Generate dynamic, explainable reasoning
            if existing_skills:
                matching_sample = ", ".join(existing_skills[:3])
                reason = (
                    f"Recommended because your skills in {matching_sample} "
                    f"show a strong alignment with the core requirements of a {career_title}."
                )
                if request.preferred_domain.lower() == domain.lower():
                    reason += f" Additionally, this aligns with your preferred domain of {domain}."
            else:
                reason = (
                    f"This career matches your academic background and general profile. "
                    f"Developing technical skills in {career_title} standard tools will further boost your fit."
                )

            # 6. Generate suggested learning resources/areas
            suggested_learning_areas = []
            for skill in missing_skills[:3]:  # Top 3 missing skills
                # Generate helpful learning titles
                if skill.lower() in ["sql", "postgresql", "mysql", "oracle"]:
                    suggested_learning_areas.append(f"Master relational databases and SQL queries ({skill})")
                elif skill.lower() in ["python", "java", "c++", "go", "javascript", "typescript"]:
                    suggested_learning_areas.append(f"Take an advanced programming course in {skill}")
                elif skill.lower() in ["tensorflow", "pytorch", "deep learning", "machine learning", "scikit-learn"]:
                    suggested_learning_areas.append(f"Study Machine Learning theory and build projects using {skill}")
                elif skill.lower() in ["docker", "kubernetes", "ci/cd", "terraform", "aws", "gcp", "azure"]:
                    suggested_learning_areas.append(f"Build hands-on experience with Cloud & DevOps tools ({skill})")
                elif skill.lower() in ["figma", "sketch", "adobe xd", "user research", "wireframing"]:
                    suggested_learning_areas.append(f"Learn visual design principles and wireframing using {skill}")
                elif skill.lower() in ["product strategy", "agile", "scrum", "roadmapping"]:
                    suggested_learning_areas.append(f"Study Agile Product Management frameworks and lifecycle ({skill})")
                else:
                    suggested_learning_areas.append(f"Improve your proficiency in {skill} via certification/courses")

            # Fallback if no missing skills
            if not suggested_learning_areas:
                suggested_learning_areas.append("Keep updating your portfolio and work on real-world projects.")

            # Create recommendation detail object
            detail = RecommendationDetail(
                career=career_title,
                match_score=round(score, 1),
                existing_skills=existing_skills,
                missing_skills=missing_skills,
                reason=reason,
                suggested_learning_areas=suggested_learning_areas
            )
            recommended_details.append(detail)

            # 7. Persist recommendation in DB if user is provided and exists
            if request.user_id and db_career:
                db_user = get_db_user_by_id(db, request.user_id)
                if db_user:
                    create_recommendation(
                        db=db,
                        user_id=db_user.id,
                        career_id=db_career.id,
                        match_score=score
                    )

        return RecommendationResponse(recommendations=recommended_details)

def get_db_user_by_id(db: Session, user_id: int):
    """
    Safely get user from DB avoiding circular dependencies.
    """
    return get_user(db, user_id)
