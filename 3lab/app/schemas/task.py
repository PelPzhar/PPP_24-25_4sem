from pydantic import BaseModel

class TaskCreate(BaseModel):
    url: str
    max_depth: int

class TaskRead(BaseModel):
    id: int
    task_id: str
    url: str
    max_depth: int
    status: str
    user_id: int

    class Config:
        orm_mode = True