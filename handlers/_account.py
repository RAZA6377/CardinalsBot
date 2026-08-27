import requests


class BsAccount:
    def __init__(self, aid: str):
        self.aid = aid
        
    def get_aid_info(self):
        response = requests.get(f"https://account.thecardinal.workers.dev/{self.aid}")
        data = response.json()
        if data.get('error'):
            return None

        return data
        