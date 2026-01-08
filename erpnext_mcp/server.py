from mcp.server.fastmcp import FastMCP
from core_logic import core_process_file
import os

# Initialize FastMCP server
mcp = FastMCP("ERPNext Integration")


@mcp.tool()
def process_document_and_create_product(file_path: str) -> str:
    """
    Processes a document (Excel or PDF), extracts product information using Gemini,
    and constructs product items in ERPNext.
    
    Args:
        file_path: Absolute path to the file to be processed.
    """
    return core_process_file(file_path)


if __name__ == "__main__":
    mcp.run()
