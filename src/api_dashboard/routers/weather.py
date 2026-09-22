from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# import requests
import httpx
from api_dashboard.cache import async_ttl_cache

# ROUTER CODE
router = APIRouter(prefix="/weather",tags=["weather"])

# PYDANTIC MODEL - catches in wht data type the value is returned
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


# @router.get("",response_model=WeatherResponse)
@async_ttl_cache(ttl_seconds=60)
async def fetch_weather(cityName:str) -> dict:
    # Convert City name to lat and Long
    async with httpx.AsyncClient() as client:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = await client.get(geo_url, params ={"name":cityName,"count":1})
        geo_data = geo_response.json()

        if "results" not in geo_data or len(geo_data["results"]) ==0:
            raise HTTPException(status_code=404, detail=f"City'{cityName}' not found")
            # return {"error": f"City '{city}' not found"}    # Handle Exception properly with above code
            
        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]

        # Fetch weather for the location
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
async def get_weather(city: str):
    return await fetch_weather(city)