from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.cruds.user import create_user, get_user_by_email
from app.schemas.user import UserCreate, UserOut
from app.core.security import create_access_token
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    token = create_access_token({"sub": new_user.email})
    return {"id": new_user.id, "email": new_user.email, "token": token}

@router.post("/login/", response_model=UserOut)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}

@router.get("/users/me/", response_model=UserOut)
def read_users_me():  # Пока без проверки токена, добавим позже
    return {"id": 1, "email": "test@example.com"}  # Заглушка