from fastapi import FastAPI
from app.api import auth_routes, task_routes

app = FastAPI(title="TaskFlow")

app.include_router(auth_routes.router)
app.include_router(task_routes.router)
