from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


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
        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        user = User(
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "User created successfully"}

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
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        # Verify user exists and password is correct
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create access token
        token = create_access_token({"sub": str(user.id)})
        
        return {"access_token": token, "token_type": "bearer"}
