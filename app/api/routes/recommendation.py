from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database.connection import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Recommendations"])

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(request: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Accepts user profile features, processes them, runs predictions, 
    calculates skill gap analysis, and returns ranked recommendations.
    """
    try:
        return RecommendationService.generate_recommendations(db=db, request=request)
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating career recommendations."
        )

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Simple health check for database and API status.
    """
    try:
        # Simple query to verify db connectivity
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "AI Career Recommendation System is running"
        }
    except Exception as e:
        logger.critical(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": str(e)
        }
