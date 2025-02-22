from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Pydantic Schemas
class Location(BaseModel):
    city: str
    latitude: float
    longitude: float
    disaster_prone_to: List[str]

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    location: Location
    tasks_completed: List[str] = []
    pet_id: Optional[str] = None
    streak: int = Field(default=0, ge=0)
    points: int = Field(default=0, ge=0)

class UserResponse(User):
    id: str

class Pet(BaseModel):
    pet_id: str
    name: str
    health: int = Field(ge=0, le=100)
    fridge: List[str]
    backpack: List[str]
    tasks_completed: List[str]
    disasters_survived: List[str]

class Task(BaseModel):
    task_id: str
    name: str
    points_gained: int
    points_lost: int
    item_required: Optional[str] = None
    type: str
    status: str

class Item(BaseModel):
    picture: str
    category: str
    reduces_damage: bool

class Disaster(BaseModel):
    type: str
    severity_levels: Dict[str, Any]

class WeatherResponse(BaseModel):
    city: str
    timezone: str
    is_day: int
    current_weather: str
    weather_code: int
