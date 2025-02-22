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
    items = db["items"][0]
    if item_name in items:
        return items[item_name]
    raise HTTPException(status_code=404, detail="Item not found")