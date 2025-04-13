#from fastmcp import FastMCP
from mcp.server.fastmcp import FastMCP
import time
# Create an MCP server
mcp = FastMCP(
    name="math",
    host="127.0.0.1",
    port=5000,
    timeout=30
)
# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def devide(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a / b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    try:
        print("Starting MCP server add on 127.0.0.1:5000")
        mcp.run(transport="sse")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep (2)