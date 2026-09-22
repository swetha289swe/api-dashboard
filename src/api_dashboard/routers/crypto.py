# import requests
import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session

from api_dashboard.cache import async_ttl_cache
from api_dashboard.database import get_session
from api_dashboard.models import SearchLog, User
from api_dashboard.security import get_current_user

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
async def get_crypto_price(coin:str, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    result = await fetch_crypto(coin)
    log = SearchLog(
        endpoint="crypto",
        query=coin,
        result_summary=f"{result['coin']}: ${result['price_usd']}",
        user_id=current_user.id
    )
    session.add(log)
    session.commit()

    return result