from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict
from models import Task
from bson import ObjectId
from database import tasks_collection

router = APIRouter()

with open("db.json", "r") as file:
    db = json.load(file)

@router.get("/tasks", response_model=List[Task])
def get_tasks():
    return db["tasks"]

@router.get("/tasks/{weather_code}")
def get_tasks_with_weather_code(weather_code: str):
    tasks = []
    for task in db["tasks"]:
        # Check if the weather_code is in the weather_code list
        if weather_code in task.get("weather_code", []):  # Default to empty list if not found
            # Create a copy of the task and exclude 'weather_code' field
            task_data = task.copy()  # Copy the task
            task_data.pop("weather_code", None)  # Remove 'weather_code' from the copy
            tasks.append(task_data)
    
    return tasks

@router.get("/tasks/", response_model=Task)
def get_task(task_id: int):
    for task in db["tasks"]:
        if task["task_id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.put("/task/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task, source: str = "json"):
    if source == "json":
        for i, u in enumerate(db["tasks"]):
            if u["task_id"] == task_id:
                db["tasks"][i] = task.dict()

                with open("db.json", "w") as file:
                    json.dump(db, file, indent=4)

                return task

        raise HTTPException(status_code=404, detail="Task not found")
    
    # If source is MongoDB
    task_data = task.dict()
    result = tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": task_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"id": task_id, **task_data}
