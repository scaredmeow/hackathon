from fastapi import FastAPI
import json
from typing import List, Dict, Any

app = FastAPI()

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

@app.get("/weather", response_model=List[Dict[str, Any]])
def get_weather():
    return db["weather"]

@app.get("/weather/{city}", response_model=Dict[str, Any])
def get_city_weather(city: str):
    for weather in db["weather"]:
        if weather["city"].lower() == city.lower():
            return weather
    return {"error": "City not found"}

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
