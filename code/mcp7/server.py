import uuid
import json 
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from mcp.server.session import ServerSession


products = []

# Create an MCP server
mcp = FastMCP("Demo 🚀")

class ProductNameSchema(BaseModel):
    use_name: bool = Field(description="Would you like to use another name?")
    other_name: str = Field(description="Alternative name")



@mcp.tool()
def add(a: int, b: int) -> int:
    """Tool to add two integer numbers"""
    return a + b


@mcp.tool()
async def create_product(product_name: str, keywords: str, ctx: Context[ServerSession, None]) -> str:
    """Create a product and generate a product
        description using LLM sampling."""
  
    if product_name == 'silly':
        result = await ctx.elicit(message="Are you sure you want to name your product as silly?",
                                  schema=ProductNameSchema)

        if result.action == "accept" and result.data:
            if not result.data.use_name:
              product_name = result.data.other_name
                
                
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

