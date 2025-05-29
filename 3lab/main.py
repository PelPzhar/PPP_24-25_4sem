from fastapi import FastAPI
from app.db.base import Base, engine
from app.models.task import User, Task
from app.api import users, tasks, websocket

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.on_event("startup")
async def startup():
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы!")

@app.get("/")
async def root():
    return {"message": "Сервер работает!"}