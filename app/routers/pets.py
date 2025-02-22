from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import Pet, ItemInInventory
from bson import ObjectId

router = APIRouter()

with open("db.json", "r") as file:
    db = json.load(file)

@router.get("/pets", response_model=List[Pet])
def get_pets():
    return db["pets"]

@router.get("/pets/{pet_id}", response_model=Pet)
def get_pet(pet_id: str):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            return pet
    raise HTTPException(status_code=404, detail="Pet not found")

@router.get("/pets/{pet_id}/backpack", response_model=List[ItemInInventory])
def get_pet_backpack(pet_id: str):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            return pet["backpack"]
    raise HTTPException(status_code=404, detail="Pet not found")

@router.put("/pets/{pet_id}/backpack/{item_name}", response_model=ItemInInventory)
def update_backpack_item_quantity(pet_id: str, item_name: str, quantity: int):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            for item in pet["backpack"]:
                if item["name"] == item_name:
                    item["quantity"] = quantity
                    with open("db.json", "w") as file:
                        json.dump(db, file, indent=4)
                    return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.get("/pets/{pet_id}/fridge", response_model=List[ItemInInventory])
def get_pet_fridge(pet_id: str):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            return pet["fridge"]
    raise HTTPException(status_code=404, detail="Pet not found")

@router.put("/pets/{pet_id}/fridge/{item_name}", response_model=ItemInInventory)
def update_fridge_item_quantity(pet_id: str, item_name: str, quantity: int):
    for pet in db["pets"]:
        if pet["pet_id"] == pet_id:
            for item in pet["fridge"]:
                if item["name"] == item_name:
                    item["quantity"] = quantity
                    with open("db.json", "w") as file:
                        json.dump(db, file, indent=4)
                    return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/pets/{pet_id}", response_model=Pet)
def update_pet(pet_id: str, pet: Pet):
        for i, u in enumerate(db["pets"]):
            if u["pet_id"] == pet_id:
                db["pets"][i] = pet.dict()

                with open("db.json", "w") as file:
                    json.dump(db, file, indent=4)

                return pet

        raise HTTPException(status_code=404, detail="Task not found")
    