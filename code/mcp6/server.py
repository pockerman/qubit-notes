import uuid
import json 

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from mcp.server.session import ServerSession


products = []

# Create an MCP server
mcp = FastMCP("Demo 🚀")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Tool to add two integer numbers"""
    return a + b


@mcp.tool()
async def create_product(product_name: str, keywords: str,
    ctx: Context[ServerSession, None]) -> str:
    """Create a product and generate a product
        description using LLM sampling."""
  
    # 1. A new product is being created
 
    product = { "id": uuid.uuid4().hex, "name": product_name, "description": "" }
    prompt = f"Create a product description about {keywords}"
    # 2. Creates a sampling message and passes the prompt as the     payload
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            )
        ],
        max_tokens=100,
    )
    product["description"] = result.content.text
    products.append(product)
    # return the complete product

    print("Added product {product}")

    return json.dumps(product)

if __name__ == "__main__":
    print("MCP server is running...")
    mcp.run()

