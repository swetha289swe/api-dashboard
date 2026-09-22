import asyncio

from fastapi import APIRouter

from api_dashboard.routers.crypto import fetch_crypto
from api_dashboard.routers.github import fetch_github_user
from api_dashboard.routers.weather import fetch_weather

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(city: str, coin: str, github_username: str):
    weather_result, crypto_result, github_result = await asyncio.gather(
        fetch_weather(city),
        fetch_crypto(coin),
        fetch_github_user(github_username),
    )

    return {
        "weather": weather_result,
        "crypto": crypto_result,
        "github": github_result,
    }