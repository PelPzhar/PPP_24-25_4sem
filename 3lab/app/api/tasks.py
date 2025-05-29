from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskRead
from app.cruds.task import create_task
from app.cruds.user import get_user
from app.db.base import get_db
from app.celery.tasks import parse_website

router = APIRouter()

@router.post("/{user_id}", response_model=TaskRead)
def create_new_task(user_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_task = create_task(db, task, user_id)
    parse_website.apply_async(
        args=[task.url, task.max_depth, user_id, db_task.task_id],
        countdown=10
    )
    return db_task