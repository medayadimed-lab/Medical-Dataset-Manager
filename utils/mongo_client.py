from pymongo import MongoClient

def get_db(uri="mongodb://localhost:27017/", db_name="ml_dataset"):
    client = MongoClient(uri)
    db = client[db_name]
    return db
