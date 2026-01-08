import requests
import os

# Ensure the server is running on http://localhost:8000
# and you have "sample_products.xlsx" created (run create_sample.py first if needed)

file_path = "sample_products.xlsx"
if not os.path.exists(file_path):
    print("Generating sample file...")
    import pandas as pd
    data = {'Item Name': ['API Test Item'], 'Description': ['Via API'], 'Price': [99.0], 'UOM': ['Nos']}
    pd.DataFrame(data).to_excel(file_path, index=False)

url = "http://localhost:8000/upload"
files = {'file': open(file_path, 'rb')}

try:
    print(f"Uploading {file_path} to {url}...")
    response = requests.post(url, files=files)
    
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except:
        print("Response Text:", response.text)

except Exception as e:
    print(f"Error: {e}")
