from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_curr_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import create_user as create_usr, update_user_profile, delete_user as delete_usr, get_user as get_usr, get_user_projects as get_user_projs
import bcrypt


users_router = APIRouter()


@users_router.post("/create", status_code=201)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await create_usr(
        db,
        user_create.username,
        bcrypt.hashpw(
            user_create.password.get_secret_value().encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8"),
        user_create.email,
        user_create.tech_stack
    )
    if not res[0]:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    return res[1]


@users_router.get("/get", status_code=200)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    res = await get_usr(db, user_id)
    if not res[0]:
        raise HTTPException(status_code=404, detail="User not found")

    return res[1]["username"]


@users_router.get("/profile", status_code=200)
async def get_profile(db: AsyncSession = Depends(get_db), user_id: int = Depends(get_curr_user)):
    res = await get_usr(db, user_id)
    if not res[0]:
        raise HTTPException(status_code=404, detail="User not found")

    return res[1]


@users_router.get("/get_projects", status_code=200)
async def get_user_projects(user_id: int, db: AsyncSession = Depends(get_db)):
    res = await get_user_projs(db, user_id)
    if res[0] != 200:
        raise HTTPException(status_code=res[0], detail=res[1])
    
    return res[2]


@users_router.patch("/update", status_code=200)
async def change_username(user_update: UserUpdate, db: AsyncSession = Depends(get_db), user_id : int = Depends(get_curr_user)):
    updates = user_update.model_dump(exclude_unset=True)
    status_code, detail = await update_user_profile(db, user_id, updates)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=detail)

    return detail


@users_router.delete("/delete", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_curr_user)):
    status_code, detail = await delete_usr(db, user_id, current_user_id)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=detail)
