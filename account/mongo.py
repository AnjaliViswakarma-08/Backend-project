# account/mongo.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # loads .env file

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise Exception("MONGODB_URI not set in .env")

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)

# Select database and collection
db = client["flashcard"]   # database name (can be anything)
exam_collection = db["exam"]         # your collection name

# New test subject collections
collections = {
    "dsa": db["dsa"],
    "coa": db["coa"],
    "toc": db["toc"],
    "cn": db["cn"],
    "os": db["os"],
}

# New notes collection
note_collection = {
    "notedsa": db["notedsa"],
    "notecoa": db["notecoa"],
    "notetoc": db["notetoc"],
    "notecn": db["notecn"],
    "noteos": db["noteos"],
}

# General notes collection for topic-based notes
notes_collection = db["notes"]
