# server.py
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("Demo 🚀")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Addition tool. It adds two integers"""
    return a + b


@mcp.tool()
def multiply(first: int, second: int) -> int:
    """Mulitplication tool. It multiplies two numbers"""
    return first * second


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Resource. Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


if __name__ == "__main__":
    mcp.run()
