from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    return AuthService.register_user(email, password, db)

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(email, password, db)
