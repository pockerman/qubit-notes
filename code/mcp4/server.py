# server.py
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, AsyncGenerator
from mcp.types import (
    LoggingMessageNotificationParams,
    TextContent
)


# Create an MCP server
mcp = FastMCP("Streamable DEMO")

# Add tool
@mcp.tool(description="A simple tool returning file content")
async def echo(message: str, ctx: Context) -> str:
    await ctx.info(f"Processing file 1/3:")
    await ctx.info(f"Processing file 2/3:")
    await ctx.info(f"Processing file 3/3:")
    return f"Here's the file content: {message}"

# Set up the transport as streamable HTTP.
mcp.run(transport="streamable-http")

