import os
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

# Load environment variables from .env
load_dotenv()

# Read config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ml_dataset_db")
USER_COLLECTION = os.getenv("USER_COLLECTION", "users")
DATASET_COLLECTION = os.getenv("DATASET_COLLECTION", "datasets")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "securepassword123")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def create_indexes():
    db[USER_COLLECTION].create_index("username", unique=True)
    db[DATASET_COLLECTION].create_index("image_id", unique=True)
    db[DATASET_COLLECTION].create_index("version")
    db[DATASET_COLLECTION].create_index("split")

def seed_admin_user():
    if db[USER_COLLECTION].find_one({"username": ADMIN_USERNAME}):
        print("✅ Admin user already exists.")
        return
    hashed_pw = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt())
    db[USER_COLLECTION].insert_one({
        "username": ADMIN_USERNAME,
        "password_hash": hashed_pw,
        "role": "admin",
        "created_at": db.command("serverStatus")["localTime"]
    })
    print("✅ Admin user created.")

def initialize_database():
    print(f"🔧 Initializing database: {DB_NAME}")
    create_indexes()
    seed_admin_user()
    print("✅ Database setup complete.")

if __name__ == "__main__":
    initialize_database()
