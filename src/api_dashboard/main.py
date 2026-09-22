from fastapi import FastAPI, HTTPException

from api_dashboard.database import create_db_and_tables
from api_dashboard.routers import auth, crypto, dashboard, github, history, weather

# from pydantic import BaseModel
# import requests
# 
app = FastAPI(title="API Dashboard")

app.include_router(auth.router)
app.include_router(weather.router)
app.include_router(crypto.router)
app.include_router(github.router)
app.include_router(dashboard.router)

app.include_router(history.router)

# DB
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
# DB


@app.get("/")
def read_root():
    return {"message":"Hello World"}

# RUN CMD
# uv run uvicorn api_dashboard.main:app --reload
