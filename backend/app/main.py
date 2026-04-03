from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/healthcheck")
async def health_check():
    return "health check"