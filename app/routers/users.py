from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import User
from bson import ObjectId
from database import users_collection

router = APIRouter()

with open("db.json", "r") as file:
    db = json.load(file)

@router.get("/users", response_model=List[User])
def get_users(source: str = "json"):
    if source == "json":
        return db["users"]
    users = list(users_collection.find())
    return [{"id": str(user["_id"]), **user} for user in users]

@router.get("/users/{user_id}", response_model=User)
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

@router.post("/users", response_model=User)
def create_user(user: User, source: str = "json"):
    if source == "json":
        db["users"].append(user.dict())
        return user
    user = user.model_dump()
    user.pop("id")
    inserted_id = users_collection.insert_one(user).inserted_id
    return {"id": str(inserted_id), **user}

@router.delete("/users/{user_id}", response_model=Dict[str, str])
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

@router.put("/users/{user_id}", response_model=User)
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
