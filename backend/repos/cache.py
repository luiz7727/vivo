import threading

from pymongo import MongoClient
from pymongo.collection import Collection
from bson import json_util
from bson import BSON
import json

from conf import mongodb_uri


cache_lock = threading.Lock()


def open_cache() -> Collection:
    with cache_lock:
        try:
            # Create a MongoClient instance
            client = MongoClient(mongodb_uri)

            # Check connection
            server_info = (
                client.server_info()
            )  # This will raise an exception if unable to connect
            print("[CACHE] Connected to MongoDB cluster.")

            # Access the 'test' database
            db = client.MapVIVO
            return db.get_collection("cache")
        except ConnectionError as e:
            print(f"[CACHE] Error connecting to MongoDB: {e}")
            return None

cache = open_cache()


# Check cache access
def checkCache():
    return open_cache() != None


# Read All
def getAll():
    # cache = open_cache()
    if cache is None:
        return [], False
    try:
        return (
            json.loads(json_util.dumps([document for document in cache.find({})])),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False


# Read
def get(cliente):
    # cache = open_cache()
    if cache is None:
        return [], False
    try:
        return (
            json.loads(
                json_util.dumps([document for document in cache.find({"id": cliente})])
            ),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False


# Write


def save(id, content):
    # cache = open_cache()
    with cache_lock:
        if cache is None:
            return False
        try:
            res = cache.replace_one({"id": id}, content, upsert=True)
            # res = cache.insert_one(content)
            return res.upserted_id , True
        except Exception as e:
            print(f"Error saving entry: {e}")
            return e, False


# Update


def update(cliente, content):
    # cache = open_cache()
    try:
        res = cache.update_one({"id": cliente}, content, upsert=True)
        return res.acknowledged
    except Exception as e:
        return False


# Delete
def delete(cliente):
    # cache = open_cache()
    res = cache.delete_one(filter={"id": cliente})
    return res.acknowledged
