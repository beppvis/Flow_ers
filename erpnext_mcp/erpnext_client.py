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

        if not self.url:
            raise ValueError("Missing FRAPPE_URL in .env")

        # Initialize FrappeClient
        self.client = FrappeClient(self.url)
        
        # For multi-tenant Frappe, we need to set the Host header to the site name
        # This tells ERPNext which site to serve
        if not hasattr(self.client.session, 'headers'):
            self.client.session.headers = {}
        
        # Set the Host header to the site name
        # This is required for multi-tenant Frappe installations
        self.client.session.headers['Host'] = 'frontend'
        
        # Now login with the site-aware session
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

            # Ensure Item Group exists
            if "item_group" in item_data and item_data["item_group"]:
                self._ensure_item_group_exists(item_data["item_group"])

            # Ensure UOM exists
            if "stock_uom" in item_data and item_data["stock_uom"]:
                self._ensure_uom_exists(item_data["stock_uom"])

            item_data["doctype"] = "Item"
            doc = self.client.insert((item_data))
            return {"status": "success", "data": doc}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _ensure_item_group_exists(self, group_name):
        doc = None
        try:
            doc = self.client.get_doc("Item Group", group_name)
        except Exception:
            pass

        if not doc:
            try:
                print(f"Creating missing Item Group: {group_name}")
                new_group = {
                    "doctype": "Item Group",
                    "item_group_name": group_name,
                    "parent_item_group": "All Item Groups",
                    "is_group": 0
                }
                return self.client.insert(new_group)
            except Exception as e:
                print(f"Failed to create Item Group {group_name}: {e}")
                pass

    def _ensure_uom_exists(self, uom_name):
        doc = None
        try:
            doc = self.client.get_doc("UOM", uom_name)
        except Exception:
            pass

        if not doc:
            try:
                print(f"Creating missing UOM: {uom_name}")
                new_uom = {
                    "doctype": "UOM",
                    "uom_name": uom_name,
                    "must_be_whole_number": 1 if uom_name in ['Nos', 'Box', 'Set'] else 0
                }
                return self.client.insert(new_uom)
            except Exception as e:
                print(f"Failed to create UOM {uom_name}: {e}")
                pass

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
