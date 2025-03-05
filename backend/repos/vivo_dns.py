from pymongo import MongoClient
from pymongo.collection import Collection
from bson import json_util
import json
import threading
from conf import mongodb_uri
import utils
from datetime import datetime

"""
obj = {
    user_id: number,
    in_cache: bool,
    last_seen: date
}
"""

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
            print("[DNS] Connected to MongoDB cluster.")

            db = client.MapVIVO
            return db.get_collection("DNS")
        except ConnectionError as e:
            print(f"[DNS] Error connecting to MongoDB: {e}")
            return None


updatable = open_db()


# Read All
def getAll():
    # updatable = open_db()
    if updatable is None:
        return [], False
    try:
        return (
            json.loads(json_util.dumps([document for document in updatable.find({})])),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False


# Read
def get(name: str):
    # updatable = open_db()
    if updatable is None:
        return [], False
    try:
        return (
            json.loads(
                json_util.dumps(
                    [document for document in updatable.find({"name": name})]
                )
            ),
            True,
        )
    except Exception as e:
        print(f"Error reading all entries: {e}")
        return [], False


# Write


def add(content):
    # updatable = open_db()
    if updatable is None:
        return False
    try:
        ping, ok = utils.ping(content["address"])
        dns = {
            "name": content["name"],
            "address": content["address"],
            "ping": ping,
            "checked_on": datetime.now().strftime("%d/%m/%Y"),
        }
        updatable.replace_one({"name": content["name"]}, dns, upsert=True)
        return True
    except:
        return False


# Update


def update(name: str, content):
    # updatable = open_db()
    if updatable is None:
        return False
    try:
        updatable.replace_one({"name": name}, content)
        return True
    except Exception as e:
        print(e)
        return False


# Delete
def delete(name):
    # updatable = open_db()
    if updatable is None:
        return False
    try:
        updatable.delete_one(filter={"name": name})
        return True
    except:
        return False