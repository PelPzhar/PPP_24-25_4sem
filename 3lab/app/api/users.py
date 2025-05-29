from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.cruds.user import create_user
from app.db.base import get_db

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)