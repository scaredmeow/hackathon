from fastapi import FastAPI, HTTPException
import json
from typing import List, Dict, Any, Optional
import httpx
from models import Pet, Task, Item, Disaster, WeatherResponse, FixedWeatherResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routers import users, tasks, items, pets

load_dotenv(".env", override=True)

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(items.router)
app.include_router(pets.router)

# Load JSON data
with open("db.json", "r") as file:
    db = json.load(file)

@app.get("/disasters", response_model=Dict[str, Dict])
def get_disasters():
    return db["disasters"][0]

# WMO Weather Codes Mapping
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# app get location weather
@app.get("/weather/fixed", response_model=FixedWeatherResponse)
async def get_location_weather(city: str, timezone: Optional[str] = "Asia/Singapore"):
    # get weathers from db.json
    weathers = db["weather"]

    # Find the weather data for the specified city
    weather = next((w for w in weathers if w["city"].lower() == city.lower()), None)
    if not weather:
        raise HTTPException(status_code=404, detail="City not found")

    return FixedWeatherResponse(
        city=weather["city"],
        timezone=weather["timezone"],
        current_weather=weather["current_weather"],
        weather_code=weather["weather_code"],
        is_day=weather["is_day"],
        background=weather["background"]
    )


@app.get("/weather", response_model=WeatherResponse)
async def get_weather(city: str, timezone: Optional[str] = "Asia/Singapore"):
    """
    Fetch current weather data for the specified latitude and longitude.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"city": city, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching geolocation data")
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail="City not found")
    latitude = data[0]["lat"]
    longitude = data[0]["lon"]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "timezone": timezone
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching weather data")
        data = response.json()
        weather_code = str(data["current_weather"].get("weather_code", 0))
        weather_description = WMO_WEATHER_CODES.get(int(weather_code), "Unknown weather condition")
        is_day = data["current_weather"].get("is_day", 1)

        return WeatherResponse(
            city=city,
            timezone=data["timezone"],
            current_weather=weather_description,
            weather_code=weather_code,
            is_day=is_day
        )
