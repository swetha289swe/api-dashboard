from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# import requests
import httpx
from api_dashboard.cache import async_ttl_cache

router = APIRouter(prefix="/crypto", tags=["crypto"])


class CryptoResponse(BaseModel):
    coin: str
    price_usd: float


# @router.get("/{coin}", response_model=CryptoResponse)
@async_ttl_cache(ttl_seconds=30)
async def fetch_crypto(coin: str) -> dict:
    async with httpx.AsyncClient() as client:
        url = "https://api.coingecko.com/api/v3/simple/price"
        response = await client.get(url, params={"ids": coin, "vs_currencies": "usd"})
        data = response.json()

        if coin not in data:
            raise HTTPException(status_code=404, detail=f"Coin '{coin}' not found")

        return {
            "coin": coin,
            "price_usd": data[coin]["usd"],
        }


@router.get("/{coin}", response_model = CryptoResponse)
async def get_crypto_price(coin:str):
    return await fetch_crypto(coin)