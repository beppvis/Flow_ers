import pandas as pd
import os

data = {
    'Item Name': ['Test Widget A', 'Test Widget B'],
    'Description': ['A high quality widget', 'Another widget'],
    'Price': [100.0, 250.50],
    'UOM': ['Nos', 'Nos']
}

df = pd.DataFrame(data)
df.to_excel('sample_products.xlsx', index=False)
print("Created sample_products.xlsx")
