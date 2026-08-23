import requests
import os
from dotenv import load_dotenv

load_dotenv()
api = os.getenv('BS_API_KEY')


headers = {
    "Authorization": f"Bearer {api}",
    "Content-Type": "application/json",
    "User-Agent": "RaZa"
}

class BsAccount:
    def __init__(self, aid: str):
        self.aid = aid
        
    @staticmethod
    def get_aid(self):
        response = requests.get(f"https://www.ballistica.net/api/v1/accounts/{self.aid}", headers=headers)
        data = response.json()
        return data