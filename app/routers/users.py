from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import User
from bson import ObjectId
from database import users_collection

router = APIRouter()

with open("db.json", "r") as file:
    db = json.load(file)

@router.get("/users", response_model=Dict[str, User])
def get_users():
    return db["users"][0]  # Since users are wrapped in a list

@router.get("/users/{username}", response_model=User)
def get_user(username: str):
    users = db["users"][0]
    if username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[username]

@router.post("/users/{username}", response_model=User)
def create_user(username: str, user: User, source: str = "json"):
    if source == "json":
        users = db["users"][0]
        if username in users:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        users[username] = user.model_dump()
        
        # Write changes back to the JSON file
        with open("db.json", "w") as file:
            json.dump(db, file, indent=4)
            
        return user
    
    # If source is MongoDB
    user_data = user.model_dump()
    user_data["username"] = username
    inserted_id = users_collection.insert_one(user_data).inserted_id
    return user_data

@router.delete("/users/{username}", response_model=Dict[str, str])
def delete_user(username: str, source: str = "json"):
    if source == "json":
        users = db["users"][0]
        if username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        
        del users[username]
        
        # Write changes back to the JSON file
        with open("db.json", "w") as file:
            json.dump(db, file, indent=4)
            
        return {"message": "User deleted successfully"}
    
    result = users_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.put("/users/{username}", response_model=User)
def update_user(username: str, user: User, source: str = "json"):
    if source == "json":
        users = db["users"][0]
        if username not in users:
            raise HTTPException(status_code=404, detail="User not found")
        
        users[username] = user.model_dump()
        
        # Write changes back to the JSON file
        with open("db.json", "w") as file:
            json.dump(db, file, indent=4)
            
        return user
    
    # If source is MongoDB
    user_data = user.model_dump()
    result = users_collection.update_one(
        {"username": username}, 
        {"$set": user_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_data
