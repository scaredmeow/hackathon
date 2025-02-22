from fastapi import FastAPI, HTTPException
import json
from typing import List, Dict, Any, Optional
import httpx
from models import Pet, Task, Item, Disaster, WeatherResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routers import users

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

# Load JSON data
with open("db.json", "r") as file:
    db = json.load(file)

@app.get("/pets", response_model=List[Pet])
def get_pets():
    return db["pets"]

@app.get("/pets/{pet_id}", response_model=Pet)
def get_pet(pet_id: str):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            return pet
    raise HTTPException(status_code=404, detail="Pet not found")

@app.get("/disasters", response_model=List[Disaster])
def get_disasters():
    return db["disasters"]

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return db["tasks"]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    for task in db["tasks"]:
        if task["task_id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/items", response_model=Dict[str, Item])
def get_items():
    return db["items"][0]  # Since items are wrapped in a list

@app.get("/items/{item_name}", response_model=Item)
def get_item(item_name: str):
    items = db["items"][0]
    if item_name in items:
        return items[item_name]
    raise HTTPException(status_code=404, detail="Item not found")

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
        weather_code = data["current_weather"].get("weather_code", 0)
        weather_description = WMO_WEATHER_CODES.get(weather_code, "Unknown weather condition")
        is_day = data["current_weather"].get("is_day", 1)

        return WeatherResponse(
            city=city,
            timezone=data["timezone"],
            current_weather=weather_description,
            weather_code=weather_code,
            is_day=is_day
        )
