from fastapi import FastAPI
from app.api import auth, tasks

app = FastAPI(title="TaskFlow")

app.include_router(auth.router)
app.include_router(tasks.router)
