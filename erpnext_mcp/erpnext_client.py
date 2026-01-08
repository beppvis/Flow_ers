import json
import os
from frappeclient import FrappeClient
from dotenv import load_dotenv

load_dotenv()


class ERPNextClient:
    def __init__(self):
        self.url = os.getenv("FRAPPE_URL")
        self.api_key = os.getenv("FRAPPE_API_KEY")
        self.api_secret = os.getenv("FRAPPE_API_SECRET")

        if not all([self.url, self.api_key, self.api_secret]):
            raise ValueError("Missing ERPNext credentials in .env")

        # self.client = FrappeClient(self.url,self.api_key, self.api_secret)
        self.client = FrappeClient(self.url)
        self.client.login("Administrator", "admin")

    def create_item(self, item_data):
        """
        Creates an Item in ERPNext.
        item_data: dict containing item details.
                   Required fields usually: item_code, item_name, item_group, stock_uom
        """
        try:
            # Check if item exists to avoid duplicates (optional, but good practice)
            if item_data["item_code"]:
                try:
                    exists = self.client.get_doc(
                        "Item", item_data["item_code"])
                    if exists:
                        return {"status": "skipped", "message": f"Item {item_data['item_code']} already exists", "data": exists}
                except Exception:
                    print("Oh no cant insert")
                    # Not found or error, proceed to create
                    pass

            item_data["doctype"] = "Item"
            doc = self.client.insert((item_data))
            return {"status": "success", "data": doc}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_item(self, item_code):
        try:
            return self.client.get_doc("Item", item_code)
        except Exception as e:
            return None

    def call_api(self, method: str, params: dict = None, http_method: str = "POST"):
        """
        Call a whitelisted Frappe API method.
        """
        try:
            if http_method.upper() == "GET":
                return self.client.get_api(method, params or {})
            else:
                return self.client.post_api(method, params or {})
        except Exception as e:
            return {"status": "error", "message": str(e)}
