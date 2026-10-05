from fastapi import APIRouter, Depends, Query, HTTPException
import httpx
from app.services.ai_service import AiClient, AiResponseError


ai_router = APIRouter()


@ai_router.post(path="/create", status_code=201)
async def generate_tasks(context: str = Query(min_length=1, max_length=10000), ai_client: AiClient = Depends(AiClient)):
    try:
        res = await ai_client.generate(context)
        return res
    except AiResponseError:
        raise HTTPException(status_code=503, detail="AI service returned an invalid response")
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="AI service unavailable")