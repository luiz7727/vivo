from datetime import datetime
import requests
import concurrent.futures

curr = datetime.now().date()

back_url = "http://nginx:8080"

format = "%d/%m/%Y"


def fetchUsers():
    url = f"{back_url}/updatable/all"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            body = r.json()
            clients = body["contents"]
            return clients
        else:
            return []
    except Exception as e:
        return []


def deleteClient(id):
    url = f"{back_url}/updatable/delete?user_id={id}"

    try:
        r = requests.delete(url)
        if r.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False


def deleteCache(id):
    url = f"{back_url}/cache/delete?user_id={id}"

    try:
        r = requests.delete(url)
        if r.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False


def process_client(client):
    user_id = client["user_id"]
    last_seen = client["last_seen"]
    covn = datetime.strptime(last_seen, format).date()
    if curr >= covn:
        print(f"[{datetime.now().strftime(format)}] User #{user_id} passed the check")
        okClient = deleteClient(user_id)
        okCache = deleteCache(user_id)
        ok = okClient and okCache
        print(
            f"[{datetime.now().strftime(format)}] User #{user_id} deleted"
            if ok
            else f"[{datetime.now().strftime(format)}] Unable to delete user #{user_id}"
        )


def main():
    print(f"[{datetime.now().strftime(format)}] Starting cleanup...")

    clients = fetchUsers()
    print(f"[{datetime.now().strftime(format)}] Got {len(clients)} users")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_client, client) for client in clients]

        # Optionally, wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            # Handle exceptions if any
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")
