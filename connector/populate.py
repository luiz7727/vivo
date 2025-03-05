import requests
from faker import Faker
from datetime import datetime, timedelta
import concurrent.futures
from config import back_url, mock_url, interval, format

faker = Faker()

epoch = datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return int((dt - epoch).total_seconds()) * 1000.0

def fetchUsers():
    url = f"{back_url}/updatable/all"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            body = r.json()
            # print(body)
            clients = body["contents"]
            return clients
        else:
            return []
    except Exception as e:
        return []


def fetchProducts(id):
    url = mock_url % id
    res = {}
    try:
        r = requests.get(url=url)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def updateConnector(status):
    url = f"{back_url}/dashboard/connector/run"
    now = datetime.now()
    next_run = now + timedelta(seconds=interval)
    
    payload = {
        "last_run": unix_time_millis(datetime.now()),
        "next_run": unix_time_millis(next_run),
        "ok": status
    }

    r = requests.post(url, json=payload)
    print(r.status_code)


def saveData(id, content):
    url = f"{back_url}/cache/save"
    update_url = f"{back_url}/updatable/update"
    payload = {"contents": content}
    try:
        r = requests.post(url, json=payload)
        ok_cache = r.status_code == 200
        if ok_cache:
            print(f"Cache atualizado com sucesso para #{id}")

            up_payload = {
                "user_id": id,
                "contents": {
                    "in_cache": True,
                    "last_seen": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                },
            }
            ru = requests.put(update_url, json=up_payload)
            ok_update = ru.status_code == 200
            
            if ok_update == 200:
                print(f"[{datetime.now().strftime(format)}] Updated clients database")
            else:
                print(
                    f"[{datetime.now().strftime(format)}] Unable to update clients DB: {ru.status_code}"
                )
        else:
            print(f"[{datetime.now().strftime(format)}]Unable to update cache...")
        return (ok_cache and ok_update)
    except Exception as e:
        print(e)
        print(f"[{datetime.now().strftime(format)}] Unable to connect to the backend")
        return False

def process_client(client):
    user_id = client["user_id"]
    in_cache = client["in_cache"]
    shards = client["shards"]
    # print(user_id, in_cache, shards)

    print(f"Updating #{user_id}")
    if in_cache is False:
        products = fetchProducts(user_id, shards)
        if len(products) > 0:
            return saveData(user_id, products)
    else:
        print(
            f"[{datetime.now().strftime(format)}] User #{user_id} already in cache, skipping"
        )
    return True


def main():
    print(f"[{datetime.now().strftime(format)}] Fetching users...")

    clients = fetchUsers()
    print(f"[{datetime.now().strftime(format)}] Got {len(clients)} users")

    if len(clients) == 0:
        print(f"[{datetime.now().strftime(format)}] Nothing to do!")
    else:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_client, client) for client in clients]

            # Optionally, wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()  # Fetch result to catch exceptions
                    results.append(res)
                    print(res)
                except Exception as e:
                    print(f"An error occurred: {e}")
    ok = results.count(False) >= 0
    updateConnector(ok)

    now = datetime.now()
    now_plus_x = now + timedelta(seconds=interval)
    print(
        f"[{datetime.now().strftime(format)}] Connector ended! Next run: {now_plus_x.strftime(format)}"
    )

