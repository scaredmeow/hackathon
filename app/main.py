from fastapi import FastAPI, HTTPException
import json
from typing import List, Dict, Any, Optional
import httpx
from schemas import Location, User, Pet, Task, Item, Disaster, WeatherResponse
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

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
# MongoDB Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["bluehacks"]
users_collection = db["users"]

# Load JSON data
with open("db.json", "r") as file:
    db = json.load(file)

@app.get("/users", response_model=List[User])
def get_users(source: str = "json"):
    if source == "json":
        return db["users"]
    users = list(users_collection.find())
    return [{"id": str(user["_id"]), **user} for user in users]

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, source: str = "json"):
    if source == "json":
        for user in db["users"]:
            if user["id"] == user_id:
                return user
    elif source == "mongodb":
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return {"id": str(user["_id"]), **user}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", response_model=User)
def create_user(user: User, source: str = "json"):
    if source == "json":
        db["users"].append(user.dict())
        return user
    inserted_id = users_collection.insert_one(user.dict()).inserted_id
    return {"id": str(inserted_id), **user.dict()}

@app.delete("/users/{user_id}", response_model=Dict[str, str])
def delete_user(user_id: str, source: str = "json"):
    if source == "json":
        for i, user in enumerate(db["users"]):
            if user["id"] == user_id:
                db["users"].pop(i)
                return {"message": "User deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: User, source: str = "json"):
    if source == "json":
        for i, u in enumerate(db["users"]):
            if u["id"] == user_id:
                db["users"][i] = user.dict()
                return user
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.dict()
    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **user_data}

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
