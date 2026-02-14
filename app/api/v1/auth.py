from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.auth_service import AuthService
from app.core.logging import setup_logger
from pydantic import BaseModel

logger = setup_logger(__name__, log_file="logs/auth.log")
router = APIRouter(prefix="/auth", tags=["Auth"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {user.email}")
    try:
        result = AuthService.register_user(user.email, user.password, db)
        logger.info(f"User registered successfully: {user.email}")
        return result
    except HTTPException as e:
        logger.warning(f"Registration failed for {user.email}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user.email}: {str(e)}", exc_info=True)
        raise

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        # Note: OAuth2PasswordRequestForm fields are username and password. 
        # We treat 'username' as the email during authentication.
        result = AuthService.authenticate_user(form_data.username, form_data.password, db)
        logger.info(f"User logged in successfully: {form_data.username}")
        return result
    except HTTPException:
        # Standardize the error response for OAuth2
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during login for {form_data.username}: {str(e)}", exc_info=True)
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
