# db.py
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from info import *


# Connect to MongoDB
try:
    client = MongoClient(DATABASE_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Test connection
    print("✅ MongoDB connected!")
except ConnectionFailure as e:
    print("❌ MongoDB connection failed:", e)
    exit(1)

db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

# --- Functions for Bot Use ---

def set_autodelete(chat_id: int, seconds: int):
    """Insert or update auto-delete setting for a chat."""
    col.update_one(
        {"chat_id": chat_id},
        {"$set": {"seconds": seconds}},
        upsert=True
    )

def get_autodelete(chat_id: int):
    """Get auto-delete time for a chat."""
    rec = col.find_one({"chat_id": chat_id})
    return rec["seconds"] if rec else None
