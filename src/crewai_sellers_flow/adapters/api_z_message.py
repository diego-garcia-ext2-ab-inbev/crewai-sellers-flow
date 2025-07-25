import requests
import os

class ApiZMessage:
    def __init__(self):
        self.api_key = os.getenv("API_Z_MESSAGE_API_KEY")
        self.base_url = os.getenv("API_Z_MESSAGE_BASE_URL")
        self.headers = {
            "client-token": self.api_key
        }

    def send_message(self, phone: str, message: str, instance: str, token: str):
        url = f"{self.base_url}/instances/{instance}/token/{token}/send-text"
        data = {
            "phone": phone,
            "message": message
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def send_image(self, phone: str, image_base64: str, instance: str, token: str):
        url = f"{self.base_url}/instances/{instance}/token/{token}/send-image"
        data = {
            "phone": phone,
            "image": image_base64,
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
