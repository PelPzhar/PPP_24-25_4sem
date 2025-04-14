from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.parser import router as parser_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(parser_router)