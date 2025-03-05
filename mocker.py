import requests
import random
import winsound


back_url = "http://localhost:5000"

amount = 20
shards = ["mobile", "fibra", "landline", "television"]

frequency = 2500  # Set Frequency To 2500 Hertz
duration = 100  # Set Duration To 1000 ms == 1 second

for i in range(301, 301 + amount):
    payload = {
        "user_id": i,
        "shards": random.choices(population=shards, k=2),
    }
    print(payload)
    r = requests.post(f"{back_url}/updatable/add", json=payload)
    if r.status_code == 200:
        print("Updatable added")
    else:
        print("Failed to add")
    winsound.Beep(frequency, duration)

winsound.Beep(3000, 1000)
