from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.projects import project_router
from app.api.users import users_router
from app.api.auth import auth_router


app = FastAPI(title="evolved project manager")


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']               
)


app.include_router(project_router, prefix="/api/projects", tags=["projects"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])


@app.get("/healthcheck")
async def health_check():
    return "health check"