from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    token: Optional[str] = None  # Добавляем token как опциональное поле

    class Config:
        orm_mode = True