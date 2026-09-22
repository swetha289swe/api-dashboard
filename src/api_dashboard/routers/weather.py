# # import requests
# import httpx
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel

# # DB
# from sqlmodel import Session

# from api_dashboard.cache import async_ttl_cache
# from api_dashboard.database import get_session
# from api_dashboard.models import SearchLog

# # ROUTER CODE
# router = APIRouter(prefix="/weather",tags=["weather"])

# # PYDANTIC MODEL - catches in wht data type the value is returned
# class CurrentWeather(BaseModel):
#     temperature: float
#     windspeed: float
#     weathercode: int
#     time: str


# class WeatherResponse(BaseModel):
#     city: str
#     country: str | None
#     latitude: float
#     longitude: float
#     current_weather: CurrentWeather


# # @router.get("",response_model=WeatherResponse)
# @async_ttl_cache(ttl_seconds=60)
# async def fetch_weather(city:str) -> dict:
#     # Convert City name to lat and Long
#     async with httpx.AsyncClient() as client:
#         geo_url = "https://geocoding-api.open-meteo.com/v1/search"
#         geo_response = await client.get(geo_url, params ={"name":city,"count":1})
#         geo_data = geo_response.json()

#         if "results" not in geo_data or len(geo_data["results"]) ==0:
#             raise HTTPException(status_code=404, detail=f"City'{city}' not found")
#             # return {"error": f"City '{city}' not found"}    # Handle Exception properly with above code
            
#         location = geo_data["results"][0]
#         latitude = location["latitude"]
#         longitude = location["longitude"]

#         # Fetch weather for the location
#         weather_url = "https://api.open-meteo.com/v1/forecast"
#         weather_response = await client.get(
#             weather_url,
#             params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "current_weather": True,
#             },
#         )
#         weather_data = weather_response.json()

#         return {
#             "city": location["name"],
#             "country": location.get("country"),
#             "latitude": latitude,
#             "longitude": longitude,
#             "current_weather": weather_data.get("current_weather"),
#         }


# @router.get("", response_model=WeatherResponse)
# async def get_weather(city: str, session: Session = Depends(get_session)):  # noqa: B008
#     result =  await fetch_weather(city)

#     log = SearchLog(
#         endpoint="weather",
#         query=city,
#         result_summary=f"{result['city']}: {result['current_weather']['temperature']}°C",
#     )
#     session.add(log)
#     session.commit()

#     return result

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
import httpx

from api_dashboard.cache import async_ttl_cache
from api_dashboard.database import get_session
from api_dashboard.models import SearchLog, User
from api_dashboard.security import get_current_user
router = APIRouter(prefix="/weather", tags=["weather"])


class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float
    weathercode: int
    time: str


class WeatherResponse(BaseModel):
    city: str
    country: str | None
    latitude: float
    longitude: float
    current_weather: CurrentWeather


@async_ttl_cache(ttl_seconds=1)
async def fetch_weather(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = await client.get(geo_url, params={"name": city, "count": 1})
        geo_data = geo_response.json()

        if "results" not in geo_data or len(geo_data["results"]) == 0:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = await client.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
            },
        )
        weather_data = weather_response.json()

        return {
            "city": location["name"],
            "country": location.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": weather_data.get("current_weather"),
        }


@router.get("", response_model=WeatherResponse)
async def get_weather(city: str, 
session: Session = Depends(get_session),
current_user: User = Depends(get_current_user),):
    result = await fetch_weather(city)

    log = SearchLog(
        endpoint="weather",
        query=city,
        result_summary=f"{result['city']}: {result['current_weather']['temperature']}°C",
        user_id=current_user.id,
    )
    session.add(log)
    session.commit()

    return result