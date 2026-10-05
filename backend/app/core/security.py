from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
import datetime
from .config import settings


oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_curr_user(token: str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        if payload.get("exp") < datetime.datetime.now(datetime.timezone.utc).timestamp():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return int(user_id)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    

def create_token(user_id):
    payload = { "sub": str(user_id),
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
                "iat": datetime.datetime.now(datetime.timezone.utc) }
    return jwt.encode(payload, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM)