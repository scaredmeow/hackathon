from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import Pet
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

@router.put("/pets/{pet_id}", response_model=Pet)
def update_pet(pet_id: str, pet: Pet):
        for i, u in enumerate(db["pets"]):
            if u["pet_id"] == pet_id:
                db["pets"][i] = pet.dict()

                with open("db.json", "w") as file:
                    json.dump(db, file, indent=4)

                return pet

        raise HTTPException(status_code=404, detail="Task not found")
    