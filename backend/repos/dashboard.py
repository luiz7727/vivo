from pymongo import MongoClient
from pymongo.collection import Collection
from bson import json_util
import json
import threading
from conf import mongodb_uri


cache_lock = threading.Lock()


def open_db() -> Collection:
    with cache_lock:
        try:
            # Create a MongoClient instance
            client = MongoClient(mongodb_uri)

            # Check connection
            server_info = (
                client.server_info()
            )  # This will raise an exception if unable to connect
            print("[connector] Connected to MongoDB cluster.")

            db = client.MapVIVO
            return db.get_collection("connector")
        except ConnectionError as e:
            print(f"[connector] Error connecting to MongoDB: {e}")
            return None


connector = open_db()


# Read All

def getAll():
    if connector is None:
        return [], False
    try:
        return (
            json.loads(
                json_util.dumps(connector.find())
            ),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False

def last():
    # connector = open_db()
    if connector is None:
        return [], False
    try:
        return (
            json.loads(
                json_util.dumps(connector.find().limit(1).sort([("$natural", -1)]))
            ),
            True,
        )
    except Exception as e:
        print(f"Error reading last run: {e}")
        return [], False


def successful():
    if connector is None:
        return [], False
    try:
        return (
            json.loads(
                json_util.dumps(connector.find({"ok": True}))
            ),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False

# Write

"""
    {
        "last_run":"date",
        "next_run":"date",
        "successful": "bool"
    }
"""


def add(content):
    # connector = open_db()
    if connector is None:
        return False
    try:
        connector.insert_one(content)
        return True
    except:
        return False
