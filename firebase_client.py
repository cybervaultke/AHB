import requests
import json
import config

class FirebaseClient:
    def __init__(self):
        # Ensure URL ends with /
        self.base_url = config.FIREBASE_DB_URL.rstrip('/')

    def get_data(self, path):
        url = f"{self.base_url}/{path.strip('/')}.json"
        response = requests.get(url)
        if response.ok:
            return response.json()
        return None

    def put_data(self, path, data):
        url = f"{self.base_url}/{path.strip('/')}.json"
        response = requests.put(url, json=data)
        return response.ok
