from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    validate_password,
    validate_email_format,
    decode_access_token
)
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/auth_service.log")

class AuthService:
    @staticmethod
    def register_user(email: str, password: str, db: Session) -> dict:
        """
        Register a new user with email and password.
        
        Args:
            email: User's email address
            password: User's plain text password
            db: Database session
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If email is invalid or already registered, or password is weak
        """
        logger.info(f"Attempting to register user: {email}")
        
        # Validate email format
        is_valid_email, result = validate_email_format(email)
        if not is_valid_email:
            logger.warning(f"Registration failed - invalid email format for {email}: {result}")
            raise HTTPException(status_code=400, detail=f"Invalid email format: {result}")
        
        # Use normalized email
        normalized_email = result
        logger.debug(f"Email normalized from {email} to {normalized_email}")
        
        # Validate password strength
        is_valid, error_message = validate_password(password)
        if not is_valid:
            logger.warning(f"Registration failed - weak password for {normalized_email}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        # Check if user already exists
        if db.query(User).filter(User.email == normalized_email).first():
            logger.warning(f"Registration failed - email already exists: {normalized_email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        try:
            user = User(
                email=normalized_email,
                hashed_password=hash_password(password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created successfully: {normalized_email} (ID: {user.id})")
            return {"message": "User created successfully"}
        except Exception as e:
            logger.error(f"Database error during user registration for {normalized_email}: {str(e)}", exc_info=True)
            db.rollback()
            raise

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> dict:
        """
        Authenticate user and return access and refresh tokens.
        
        Implements account lockout after MAX_LOGIN_ATTEMPTS failed attempts.
        
        Args:
            email: User's email address
            password: User's plain text password
            db: Database session
            
        Returns:
            dict: Access token, refresh token, and token type
            
        Raises:
            HTTPException: If credentials are invalid or account is locked
        """
        logger.info(f"Attempting to authenticate user: {email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        # Update last login attempt
        now = datetime.now(timezone.utc)
        
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user.last_login_attempt = now
        
        # Check if account is locked
        if user.locked_until and user.locked_until > now:
            time_remaining = int((user.locked_until - now).total_seconds() / 60)
            logger.warning(f"Authentication blocked - account locked for {email} (locked for {time_remaining} more minutes)")
            raise HTTPException(
                status_code=403, 
                detail=f"Account is locked due to too many failed login attempts. Try again in {time_remaining} minutes."
            )
        
        # Reset lockout if time has passed
        if user.locked_until and user.locked_until <= now:
            logger.info(f"Lockout period expired for {email}, resetting failed attempts")
            user.locked_until = None
            user.failed_login_attempts = 0
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            logger.warning(f"Authentication failed - invalid password for: {email} (attempt {user.failed_login_attempts})")
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                logger.error(f"Account locked for {email} due to {settings.MAX_LOGIN_ATTEMPTS} failed attempts (locked until {user.locked_until})")
                db.commit()
                raise HTTPException(
                    status_code=403, 
                    detail=f"Account locked due to {settings.MAX_LOGIN_ATTEMPTS} failed login attempts. Try again in {settings.ACCOUNT_LOCKOUT_MINUTES} minutes."
                )
            
            db.commit()
            remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid credentials. {remaining_attempts} attempts remaining before account lockout."
            )
        
        # Successful authentication - reset failed attempts
        if user.failed_login_attempts > 0:
            logger.info(f"Successful login for {email}, resetting failed attempts from {user.failed_login_attempts}")
            user.failed_login_attempts = 0
            user.locked_until = None
        
        db.commit()

        # Create access and refresh tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        logger.info(f"User authenticated successfully: {email} (ID: {user.id})")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> dict:
        """
        Generate a new access token using a valid refresh token.
        
        Args:
            refresh_token: The refresh token JWT
            db: Database session
            
        Returns:
            dict: New access token and token type
            
        Raises:
            HTTPException: If refresh token is invalid or user not found
        """
        logger.info("Attempting to refresh access token")
        
        # Decode and validate refresh token
        from jose import jwt, JWTError
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            # Verify this is actually a refresh token, not an access token
            if payload.get("type") != "refresh":
                logger.warning("Token refresh failed - token is not a refresh token")
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            user_id = payload.get("sub")
        except JWTError:
            user_id = None

        if not user_id:
            logger.warning("Token refresh failed - invalid refresh token")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Find user
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            logger.warning(f"Token refresh failed - user not found: {user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            logger.warning(f"Token refresh failed - user inactive: {user.email}")
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        # Generate new access token
        new_access_token = create_access_token({"sub": str(user.id)})
        logger.info(f"Access token refreshed successfully for user: {user.email} (ID: {user.id})")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
