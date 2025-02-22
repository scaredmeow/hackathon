from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx

app = FastAPI()

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

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    current_weather: str

# Load JSON data
with open("db.json", "r") as file:
    db = json.load(file)

@app.get("/users", response_model=List[Dict[str, Any]])
def get_users():
    return db["users"]

@app.get("/users/{user_id}", response_model=Dict[str, Any])
def get_user(user_id: str):
    for user in db["users"]:
        if user["id"] == user_id:
            return user
    return {"error": "User not found"}

@app.get("/pets", response_model=List[Dict[str, Any]])
def get_pets():
    return db["pets"]

@app.get("/pets/{pet_id}", response_model=Dict[str, Any])
def get_pet(pet_id: str):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            return pet
    return {"error": "Pet not found"}

@app.get("/weather", response_model=WeatherResponse)
async def get_weather(latitude: float, longitude: float, timezone: Optional[str] = "Asia/Singapore"):
    """
    Fetch current weather data for the specified latitude and longitude.
    """
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
        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "timezone": data["timezone"],
            "current_weather": weather_description
        }

@app.get("/disasters", response_model=List[Dict[str, Any]])
def get_disasters():
    return db["disasters"]

@app.get("/tasks", response_model=List[Dict[str, Any]])
def get_tasks():
    return db["tasks"]

@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
def get_task(task_id: str):
    for task in db["tasks"]:
        if task["task_id"] == task_id:
            return task
    return {"error": "Task not found"}

@app.get("/items", response_model=Dict[str, Dict[str, Any]])
def get_items():
    return db["items"][0]  # Since items are wrapped in a list

@app.get("/items/{item_name}", response_model=Dict[str, Any])
def get_item(item_name: str):
    items = db["items"][0]
    if item_name in items:
        return items[item_name]
    return {"error": "Item not found"}
