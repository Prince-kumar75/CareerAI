from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database.connection import get_db
from app.database import crud
from app.schemas.recommendation import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(feedback_in: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Stores user feedback about career recommendations.
    """
    db_career = crud.get_career_by_title(db, title=feedback_in.career_title)
    if not db_career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career role '{feedback_in.career_title}' not found in the database."
        )
        
    if feedback_in.user_id:
        db_user = crud.get_user(db, user_id=feedback_in.user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {feedback_in.user_id} not found."
            )
            
    try:
        return crud.create_feedback(
            db=db,
            user_id=feedback_in.user_id,
            career_id=db_career.id,
            rating=feedback_in.rating,
            feedback_text=feedback_in.feedback
        )
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving feedback."
        )
