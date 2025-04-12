from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.parser import parse_and_store_graph
from redis import Redis
from app.core.config import settings
from app.schemas.parser import ParseRequest

router = APIRouter()
redis_client = Redis.from_url(settings.REDIS_URL)


@router.post("/parse/")
async def parse_website(request: ParseRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    graph_data, html_graph = await parse_and_store_graph(request.url, user.id)
    return {"graph": graph_data, "message": "Graph parsed and stored",
            "visualization_key": f"graph:html:{user.id}:{request.url}"}


@router.get("/parse/visualization/{user_id}/{url:path}", response_class=HTMLResponse)
async def get_visualization(user_id: int, url: str, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this visualization")

    redis_key_html = f"graph:html:{user_id}:{url}"
    html_graph = redis_client.get(redis_key_html)
    if not html_graph:
        raise HTTPException(status_code=404, detail="Visualization not found or expired")

    return HTMLResponse(content=html_graph.decode('utf-8'))