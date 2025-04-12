from pydantic import BaseModel, HttpUrl

class ParseRequest(BaseModel):
    url: HttpUrl  # Используем HttpUrl для валидации URL