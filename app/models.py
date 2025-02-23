from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Pydantic Schemas
class Location(BaseModel):
    city: str
    latitude: float
    longitude: float
    disaster_prone_to: List[str]

class User(BaseModel):
    email: str
    location: Location
    tasks_completed: List[str] = []
    pet_name: Optional[str] = None
    streak: int = Field(default=0, ge=0)
    points: int = Field(default=0, ge=0)

class UserResponse(User):
    id: str

class Task(BaseModel):
    task_id: int
    name: str
    points_gained: int
    points_lost: int
    item_required: Optional[str] = None
    type: str
    status: str
    weather_code: List[str]

class Disaster(BaseModel):
    type: str
    severity_levels: Dict[str, Any]

class WeatherResponse(BaseModel):
    city: str
    timezone: str
    is_day: int
    current_weather: str
    weather_code: str

class FixedWeatherResponse(BaseModel):
    city: str
    timezone: str
    is_day: int
    current_weather: str
    weather_code: str
    background: str

class Item(BaseModel):
    picture: str
    category: str
    reduces_damage: bool
    quantity: int
    location: str

class Pet(BaseModel):
    pet_name: str
    health: int = Field(ge=0, le=100)
    tasks_completed: List[str]
    disasters_survived: List[str]