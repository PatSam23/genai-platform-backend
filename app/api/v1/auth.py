from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.auth_service import AuthService
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/auth.log")
router = APIRouter(prefix="/auth", tags=["Auth"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {email}")
    try:
        result = AuthService.register_user(email, password, db)
        logger.info(f"User registered successfully: {email}")
        return result
    except HTTPException as e:
        logger.warning(f"Registration failed for {email}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for {email}: {str(e)}", exc_info=True)
        raise

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {email}")
    try:
        result = AuthService.authenticate_user(email, password, db)
        logger.info(f"User logged in successfully: {email}")
        return result
    except HTTPException as e:
        logger.warning(f"Login failed for {email}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for {email}: {str(e)}", exc_info=True)
        raise

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    
    The refresh token is obtained during login and has a longer lifespan (30 days).
    Use this endpoint to get a new access token without re-entering credentials.
    """
    logger.info("Token refresh attempt")
    try:
        result = AuthService.refresh_access_token(request.refresh_token, db)
        logger.info("Access token refreshed successfully")
        return result
    except HTTPException as e:
        logger.warning(f"Token refresh failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}", exc_info=True)
        raise
