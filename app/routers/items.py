from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import Item
from bson import ObjectId

router = APIRouter()

with open("db.json", "r") as file:
    db = json.load(file)

@router.get("/items", response_model=Dict[str, Item])
def get_items():
    return db["items"][0]  # Since items are wrapped in a list

@router.get("/items/{item_name}", response_model=Item)
def get_item(item_name: str):
    for item in db["items"]:
        if item["name"] == item_name:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# get items by location
@router.get("/items/location/{location}", response_model=List[Item])
def get_items_by_location(location: str):
    return [item for item in db["items"] if item["location"] == location]