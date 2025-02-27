import requests
import json
import time

def test_server():
    url = "http://127.0.0.1:5000/upload"
    json_data = {"door_opened": [time.time()], "door_closed": [time.time()+0.5], "PIR":[time.time()+0.25]}

    with open("test.json", "w") as f:
        json.dump(json_data, f)

    with open("test.json", "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)

    print("Response:", response.json())


if __name__ == "__main__":
    while True:
        try:
            test_server()
        except:
            pass
        time.sleep(1)
