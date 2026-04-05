from pydantic import BaseModel
from datetime import datetime 


class ProjectIn(BaseModel):
    name: str
    description: str | None = None
    user_id: int # TODO: убрать отсюда, брать из токена
    is_public: bool


class ProjectOut(BaseModel):
    name: str
    description: str | None = None 
    created_at: datetime
