from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_curr_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_user as create_usr, change_username as change_usrname, delete_user as delete_usr, get_user as get_usr


users_router = APIRouter()


@users_router.post("/create", status_code=201)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await create_usr(db, user_create.username, user_create.password.get_secret_value())
    if not res[0]:
        raise HTTPException(status_code=409, detail="Username already exists")

    return res[1]


@users_router.get("/get", status_code=200)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    res = await get_usr(db, user_id)
    if not res[0]:
        raise HTTPException(status_code=404, detail="User not found")

    return res[1]["username"]


@users_router.patch("/update", status_code=200)
async def change_username(user_update: UserUpdate, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    res = await change_usrname(db, user_id, user_update.new_username)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])

    return res[1]


@users_router.delete("/delete", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_curr_user)):
    status_code, detail = await delete_usr(db, user_id, current_user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=detail)
