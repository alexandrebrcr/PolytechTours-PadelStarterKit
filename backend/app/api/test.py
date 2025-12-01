from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, engine, init_db_test
from app.models import models
from app.core.config import settings

router = APIRouter()

@router.post("/reset-db")
def reset_database():
    """Réinitialise la base de données (Uniquement en mode TESTING)"""
    if not settings.testing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reset DB only allowed in testing mode"
        )
    
    # Drop all tables
    models.Base.metadata.drop_all(bind=engine)
    
    # Re-init DB (creates tables and admin user AND test data)
    init_db_test()
    
    return {"message": "Database reset successfully"}
