from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate
import uuid

def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = Task(
        task_id=str(uuid.uuid4()),
        url=task.url,
        max_depth=task.max_depth,
        status="PENDING",
        user_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: str, status: str):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task