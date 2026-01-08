import pandas as pd
from fpdf import FPDF
import os


def generate_excel():
    data = [
        {
            "Item Code": "GADGET-001",
            "Item Name": "Super Gadget",
            "Description": "A wonderful gadget for all your needs.",
            "Item Group": "Products",
            "Stock UOM": "Nos",
            "Standard Rate": 199.99
        },
        {
            "Item Code": "WIDGET-X",
            "Item Name": "Mega Widget",
            "Description": "The heavy duty widget option.",
            "Item Group": "Raw Material",
            "Stock UOM": "Kg",
            "Standard Rate": 45.50
        }
    ]
    df = pd.DataFrame(data)
    df.to_excel("sample_data/sample_products.xlsx", index=False)
    print("Created sample_data/sample_products.xlsx")


def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    text = """
    INVOICE #12345
    
    Supplier: Tech Corp
    Date: 2024-01-08
    
    Items:
    1. Laptop Pro X1
       Code: LAP-X1
       Description: High performance laptop with 32GB RAM.
       Price: $1200
    
    2. Wireless Mouse
       Code: PERI-MSE-01
       Description: Ergonomic wireless mouse.
       Price: $25
       
    3. Monitor 4K
       Code: DISP-4K-27
       Description: 27 inch 4K display.
       Price: $350
    """

    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=1, align='L')

    pdf.output("sample_data/sample_invoice.pdf")
    print("Created sample_data/sample_invoice.pdf")


if __name__ == "__main__":
    if not os.path.exists("sample_data"):
        os.makedirs("sample_data")
    generate_excel()
    generate_pdf()
