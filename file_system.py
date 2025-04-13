import os 
from mcp.server.fastmcp import FastMCP
import time
# Create an MCP server
mcp = FastMCP(
    name="file_system",
    host="127.0.0.1",
    port=5002,
    timeout=30
)

@mcp.tool(description="list files in the directory and retuns file path and list of file")
def file_list():
    file_path = 'C:\\temp\\aitest\\'
    file_details = {'file_path': {file_path}, 'files': os.listdir(file_path) }
    return file_details

@mcp.tool(description="Read a file")
def read_file(file_path):
    """
    Reads the contents of a text file.

    Parameters:
    file_path (str): Path to the text file.

    Returns:
    str: Contents of the file as a single string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return f"file_content: {content}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@mcp.tool(description="Create New File, parameters file_name and content")
def create_new_file(file_path, content=""):
    """
    Creates a new text file and writes content to it.

    Parameters:
    file_path (str): Path where the file will be created.
    content (str): Content to write into the file (default is empty).

    Returns:
    str: Success message or error.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"File created successfully at: {file_path}"
    except Exception as e:
        return f"Failed to create file: {str(e)}"

if __name__ == "__main__":
    try:
        print("Starting MCP server add on 127.0.0.1:5002")
        mcp.run(transport="sse")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep (2)