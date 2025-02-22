from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["bluehacks"]
users_collection = db["users"]
tasks_collection = db["tasks"]

