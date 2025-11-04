import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ml_dataset_db")
DATASET_COLLECTION = os.getenv("DATASET_COLLECTION", "datasets")
USER_COLLECTION = os.getenv("USER_COLLECTION", "users")

def connect_to_mongo():
    """
    Connects to MongoDB and returns the database object.
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def get_user_collection():
    """
    Returns the user collection object.
    """
    db = connect_to_mongo()
    return db[USER_COLLECTION]

def get_dataset_collection():
    """
    Returns the dataset collection object.
    """
    db = connect_to_mongo()
    return db[DATASET_COLLECTION]
