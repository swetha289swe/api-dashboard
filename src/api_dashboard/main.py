from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import requests
from api_dashboard.routers import weather,crypto,github,dashboard

app = FastAPI(title="API Dashboard")

app.include_router(weather.router)
app.include_router(crypto.router)
app.include_router(github.router)
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    return {"message":"Hello World"}

# RUN CMD
# uv run uvicorn api_dashboard.main:app --reload
