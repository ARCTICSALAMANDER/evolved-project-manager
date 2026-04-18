from app.schemas.user import UserCreate
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from app.db.crud import create_user, check_user_data, check_refresh_token, create_refresh_token
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
        user_id = res[1]
        refresh_token = await create_refresh_token(db, user_id)
        return {"token": create_token(user_id), "refresh_token": refresh_token}
    else:
        raise HTTPException(status_code=409, detail="Username already exists")
    

@auth_router.post("/login", status_code=200)
async def login(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await check_user_data(db, 
                                user_create.username, 
                                user_create.password.get_secret_value())
    
    if res[0]:
        user_id = res[1]
        refresh_token = await create_refresh_token(db, user_id)
        return {"token": create_token(res[1]), "refresh_token": refresh_token}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    

@auth_router.post("/refresh", status_code=200)
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    is_valid_token = await check_refresh_token(refresh_token, db)

    if is_valid_token[0] != 200:
        raise HTTPException(status_code=is_valid_token[0], detail=is_valid_token[1])

    return {"token": create_token(is_valid_token[1])}
        