from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_db
from app.database import crud
from app.schemas.career import CareerResponse, CareerDetailResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/careers", tags=["Careers"])

@router.get("/", response_model=List[CareerResponse])
def list_careers(db: Session = Depends(get_db)):
    """
    Returns list of all available career roles.
    """
    try:
        return crud.get_careers(db)
    except Exception as e:
        logger.error(f"Error listing careers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching careers."
        )

@router.get("/{career_id}", response_model=CareerDetailResponse)
def get_career_details(career_id: int, db: Session = Depends(get_db)):
    """
    Returns details for a career role, including required skills and importance weights.
    """
    db_career = crud.get_career(db, career_id=career_id)
    if not db_career:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career role with ID {career_id} not found."
        )
    return db_career
