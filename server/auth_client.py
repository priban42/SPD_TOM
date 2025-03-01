import time
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# User credentials
node_id = "test"
password = "test"

# Register user (only needed once)
# register_response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
# print("Register:", register_response.json())

# Login to get token
# Send data

data_payload = {"node_id": node_id,
                "password": password,
                "elapsed_time":5,
                "timestamps": [time.time(), time.time()+10],
                "event_types":[0, 1],
                "tag_ids":[0, 0],
                "stall_ids":[0, 0]}
# data_response = requests.post(f"{BASE_URL}/data", data=json.dumps(data_payload), headers=headers)
data_response = requests.post(f"{BASE_URL}/data", json=data_payload)
print("Data response:", data_response.json())
