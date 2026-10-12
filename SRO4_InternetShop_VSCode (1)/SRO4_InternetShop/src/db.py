"""MongoDB connection and indexes."""
import os
from pymongo import MongoClient, ASCENDING, DESCENDING

def connect():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    dbname = os.getenv("MONGODB_DB", "sro4_shop")
    client = MongoClient(uri, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    return client, client[dbname]

def ensure_indexes(db):
    db.orders.create_index([("customer_id", ASCENDING), ("created_at", DESCENDING)], name="customer_date")
    db.orders.create_index([("status", ASCENDING), ("created_at", DESCENDING)], name="status_date")
    db.orders.create_index([("items.category_snapshot", ASCENDING)], name="category_snapshot")
