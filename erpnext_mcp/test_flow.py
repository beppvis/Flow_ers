import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Set mock env vars before importing modules that check them
os.environ["ERPNEXT_URL"] = "http://mock.local"
os.environ["ERPNEXT_API_KEY"] = "mock_key"
os.environ["ERPNEXT_API_SECRET"] = "mock_secret"
os.environ["GEMINI_API_KEY"] = "mock_gemini_key"

# Add current directory to sys.path
sys.path.append(os.getcwd())

from server import process_document_and_create_product

class TestMCPServer(unittest.TestCase):
    
    @patch('server.process_excel')
    @patch('server.extract_product_data')
    @patch('server.ERPNextClient')
    def test_process_excel_flow(self, MockClient, mock_extract, mock_process_excel):
        # Setup mocks
        mock_process_excel.return_value = "Mocked Excel Content"
        
        mock_extract.return_value = [
            {
                "item_code": "TEST-001",
                "item_name": "Test Item 1",
                "description": "Desc 1",
                "standard_rate": 100,
                "item_group": "Products",
                "stock_uom": "Nos",
                "is_stock_item": 1
            }
        ]
        
        mock_client_instance = MockClient.return_value
        mock_client_instance.get_item.return_value = None # Item does not exist
        mock_client_instance.create_item.return_value = {"item_code": "TEST-001", "item_name": "Test Item 1"}

        # Create dummy file
        with open("test.xlsx", "w") as f:
            f.write("dummy")

        try:
            # Run function
            result = process_document_and_create_product(os.path.abspath("test.xlsx"))
            
            # Verify interactions
            mock_process_excel.assert_called_once()
            mock_extract.assert_called_once_with("Mocked Excel Content")
            mock_client_instance.get_item.assert_called_with("TEST-001")
            mock_client_instance.create_item.assert_called_once()
            
            print("\nTest Result Output:\n", result)
            self.assertIn("Success: Created item TEST-001", result)

        finally:
            if os.path.exists("test.xlsx"):
                os.remove("test.xlsx")

if __name__ == '__main__':
    unittest.main()
