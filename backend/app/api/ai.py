from fastapi import APIRouter, Depends, Query, HTTPException
from app.services.ai_service import AiClient


ai_router = APIRouter()


@ai_router.post(path="/create", status_code=201)
def generate_tasks(context: str = Query(min_length=1, max_length=10000), ai_client: AiClient = Depends(AiClient)):
    try:
        res = ai_client.generate(context)
        return res
    except Exception as e:
        raise HTTPException(status_code=503, detail="AI service unavailable")