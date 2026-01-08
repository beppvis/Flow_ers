import requests
import json
from config import ERPNEXT_URL, ERPNEXT_API_KEY, ERPNEXT_API_SECRET

class ERPNextClient:
    def __init__(self):
        self.base_url = ERPNEXT_URL.rstrip('/')
        self.headers = {
            "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SECRET}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_item(self, item_code):
        """
        Check if an item exists in ERPNext.
        """
        url = f"{self.base_url}/api/resource/Item/{item_code}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()['data']
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching item {item_code}: {e}")
            return None

    def create_item(self, item_data):
        """
        Create a new item in ERPNext.
        """
        url = f"{self.base_url}/api/resource/Item"
        
        # Ensure item_code is strings (ERPNext requirement)
        if 'item_code' in item_data:
            item_data['item_code'] = str(item_data['item_code'])
        
        # Default item_group if not present (required field often)
        if 'item_group' not in item_data:
             item_data['item_group'] = 'All Item Groups' 

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(item_data))
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.HTTPError as e:
            print(f"Error creating item: {e}")
            print(f"Response content: {response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error creating item: {e}")
            raise
