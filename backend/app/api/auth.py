from app.schemas.user import UserCreate
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from app.db.crud import create_user, check_user_data
from app.core.security import create_token
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt


auth_router = APIRouter()


@auth_router.post("/register", status_code=201)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await create_user(db, 
                            user_create.username, 
                            bcrypt.hashpw(user_create.password.get_secret_value().encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
    if res[0]:
        return {"token": create_token(res[1])}
    else:
        raise HTTPException(status_code=409, detail="Username already exists")
    

@auth_router.post("/login", status_code=200)
async def login(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await check_user_data(db, 
                                user_create.username, 
                                user_create.password.get_secret_value())
    
    if res[0]:
        return {"token": create_token(res[1])}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
