# qubit-note: AI Series | MCP Sampling


## Overview

In this qubit-note we will be looking sampling in the context of MCP. 
In the Model Context Protocol (MCP), sampling refers to a structured way for an MCP server to ask a client’s language model to generate content, 
rather than the client directly calling the model itself.


**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, MCP-sampling, Python

## MCP Sampling

As per [1]:

_The Model Context Protocol (MCP) provides a standardized way for servers to request LLM sampling (“completions” or “generations”) from language models via clients. This flow allows clients to maintain control over model access, selection, and permissions while enabling servers to leverage AI capabilities—with no server API keys necessary. Servers can request text, audio, or image-based interactions and optionally include context from MCP servers in their prompts._

In other words, with MCP sampling the MCP server can access the LLM model on the client side in order to perform some tasks.
so within MCP the client owns the LLM whilst the server owns tools, data and workflows. Sampling allows us to:

- Servers to request LLM output
- Clients to retain control over models, prompts, and policies
- A clean boundary between logic and generation 

Typical sampling use cases include:


- Natural language generation
- Summarization
- Explanation
- Classification
- Planning or reasoning steps

Let's see how we can implement sampling:

```
# server.py

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
```


```
# client.py

from typing import Any
from mcp import ClientSession, StdioServerParameters, types
from mcp.server.fastmcp import Context
from mcp.client.stdio import stdio_client

# Create server parameters for STDIO connection
server_params = StdioServerParameters(
    command="mcp",  # Executable
    args=["run", "server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
    capabilities={
    "sampling": {} # we need to let the server know we support sampling
  }
)

async def list_resources(session: ClientSession):
    # List available resources
    resources = await session.list_resources()
    print("MCP Server resources")
    for resource in resources:
        print("Resource: ", resource)
    
async def list_tools(session: ClientSession) -> Any:
    # List available tools
    tools = await session.list_tools()
    print("MCP Server tools")
    for tool in tools.tools:
        print("Tool: ", tool.name)

    return tools
async def call_tool(tool_name: str, session: ClientSession, **tool_args) -> Any:

    # Call a tool
    print("CALL TOOL")
    result = await session.call_tool(tool_name, arguments=tool_args)
    print(result.content)

async def call_llm(prompt: str, system_prompt: str) -> str:
    return "This is a fake LLM response"

async def handle_sampling_message(context: Context, 
                                  params: types.CreateMessageRequestParams) -> types.CreateMessageResult:
    print(f"Sampling request: {params.messages}")
    # 1. parse out the incoming prompt
    message = params.messages[0].content.text
    # 2. call the llm to get a response on our prompt query
    response = await call_llm(message, "You're a helpful assistant, keep to the topic, don't make things up too much but definitely create a compelling product description")
   
    # create the sample response
    # Sampling handlers must return CreateMessageResult
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text=response,
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )





async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=handle_sampling_message) as session:

            # Initialize the connection
            await session.initialize()

            # call the create tool on the server
            # list tools
            tools = await list_tools(session)

            tool_name = tools.tools[1].name
            print(f"Using tool: {tool_name}")

            await call_tool(tool_name=tools.tools[1].name, 
                            session=session, **{"product_name": "Test Product", "keywords": "key-1, key-2"})
            

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

Open a terminal and satrt the server:

```
python server.py 
```

Yet in another terminal and run the client. Your should see the following

```
MCP Server tools
Tool:  add
Tool:  create_product
Using tool: create_product
CALL TOOL
                    INFO     Processing request of type CallToolRequest                                                                                                                                                         
Sampling request: [SamplingMessage(role='user', content=TextContent(type='text', text='Create a product description about key-1, key-2', annotations=None, meta=None))]
[TextContent(type='text', text='{"id": "ae42a08b8a2d45d2b95d6c6bd4bf846b", "name": "Test Product", "description": "This is a fake LLM response"}', annotations=None, meta=None)]

```

## Summary

In MCP, sampling is a standardized mechanism that allows an MCP server to request content generation from a client-owned language model, rather than calling the model directly. This design keeps control of model access, selection, and policies on the client side, while enabling servers to use AI capabilities without managing API keys. Sampling establishes a clear separation where servers handle tools, data, and workflows, and clients handle LLM execution. It supports text, audio, and image generation and is commonly used for tasks such as natural language generation, summarization, explanation, classification, and planning.

## References

1. <a href="https://modelcontextprotocol.io/specification/2025-06-18/client/sampling">Sampling</a>
2. Christoffer Noring _Learn Model Context Protocol with Python_, Packt