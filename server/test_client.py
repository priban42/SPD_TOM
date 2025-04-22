import time
import requests
import json
import random

BASE_URL = "http://127.0.0.1:5000"

nodes = {'T2_B3_1_0_M_3':'password',
         'T2_B2_1_1_F_1':'password'}

for i in range(5):
    time = 0
    node_id = random.choice(list(nodes.keys()))
    stall_id = random.randint(0, 2)
    data_payload = {"node_id": node_id,
                    "password": nodes[node_id],
                    "elapsed_time": 5,
                    "timestamps": [time, time+1, time+2],
                    "event_types": [0, 2, 1],
                    "tag_ids": ["00:00:00", "00:00:00", "00:00:00"],
                    "stall_ids": [stall_id, stall_id, stall_id]}
    time += 6

    data_response = requests.post(f"{BASE_URL}/data", json=data_payload)
    print("Data response:", data_response.json())
# data_response = requests.post(f"{BASE_URL}/data", data=json.dumps(data_payload), headers=headers)

