from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, validate_password
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
            HTTPException: If email is already registered
        """
        logger.info(f"Attempting to register user: {email}")
        
        # Validate password strength
        is_valid, error_message = validate_password(password)
        if not is_valid:
            logger.warning(f"Registration failed - weak password for {email}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            logger.warning(f"Registration failed - email already exists: {email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        try:
            user = User(
                email=email,
                hashed_password=hash_password(password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created successfully: {email} (ID: {user.id})")
            return {"message": "User created successfully"}
        except Exception as e:
            logger.error(f"Database error during user registration for {email}: {str(e)}", exc_info=True)
            db.rollback()
            raise

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> dict:
        """
        Authenticate user and return access token.
        
        Args:
            email: User's email address
            password: User's plain text password
            db: Database session
            
        Returns:
            dict: Access token and token type
            
        Raises:
            HTTPException: If credentials are invalid
        """
        logger.info(f"Attempting to authenticate user: {email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        # Verify user exists and password is correct
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed - invalid password for: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create access token
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"User authenticated successfully: {email} (ID: {user.id})")
        
        return {"access_token": token, "token_type": "bearer"}
