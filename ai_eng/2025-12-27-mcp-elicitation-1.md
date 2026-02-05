# qubit-note: AI Series | MCP Elicitation

## Overview

Very often the server needs additional information from the client in order to
perfrom a ceratin task. 

Elicitation is the process by which a model (or tool) actively requests additional information, clarification, or context from the user because the current context is insufficient to proceed safely or correctly. The Model Context Protocol (MCP) provides a standardized way for servers to
do this. Specifically, in MCP, elicitation is a first-class, explicit interaction pattern, not an ad-hoc follow-up question.

In this qubit-note we will discuss how to implement elicitation

**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, MCP-elicitation, Python

## MCP Elicitation

MCP is designed for:

- Tool-using models
- Long-lived context
- External memory
- Multi-step reasoning


In such settings guessing is not allowed. Therefore, the server should pause and somehow elicit the information that is missing.
In MCP, elicitation is explicit, structured request for accessing missing context. It is part of the protocol, not just conversation
and it blocks execution until resolved. All in all, MCP elicitation improves correctness, safety, and user experience.

Let's now see how to implement MCP elicitation.

### Implement elicitation

For security reasons, servers should not use elicitation in order to request sensitive information. In addition, applications
should make it clear which server is requesting the information, allow the users to review and modify their responses 
and respect user privacy and provide clear decline and cancel options [1].

The code below shows a simplified implementation of MCP elicitation:

```
# server.py

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
```

The server implementation is not very much different from what we did in <a href="2025-12-26-mcp-sampling.md">qubit-note: AI Series | MCP Sampling</a>.
The client is shown next.

```
from typing import Any
from mcp import ClientSession, StdioServerParameters, types
from mcp.server.fastmcp import Context
from mcp.client.stdio import stdio_client
from mcp.types import ElicitRequestParams, ElicitResult, TextContent

# Create server parameters for STDIO connection
server_params = StdioServerParameters(
    command="mcp",  # Executable
    args=["run", "server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
    capabilities={
    "sampling": {}, # we need to let the server know we support sampling
    "elicitation": {} # we need to let the server know we support elicitation
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

async def elicitation_callback_handler(context:Context, params: ElicitRequestParams):
    print(f"[CLIENT] Received elicitation data: {params.message}")

    return ElicitResult(action="accept", content={
         "use_name": True,
         "other_name": "INVALID"
    }) 


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, 
                                 sampling_callback=handle_sampling_message,
                                 elicitation_callback=elicitation_callback_handler) as session:

            # Initialize the connection
            await session.initialize()

            # call the create tool on the server
            # list tools
            tools = await list_tools(session)

            tool_name = tools.tools[1].name
            print(f"Using tool: {tool_name}")
            product_name = input("Enter first value: ")
            await call_tool(tool_name=tools.tools[1].name, 
                            session=session, **{"product_name": product_name.strip().lower(), "keywords": "key-1, key-2"})
            

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

The client is more involved. We need a callback to handle the eliciation as well as inform the server we can handle elicitation.
Open a terminal and satrt the server:

```
python server.py 
```

Yet in another terminal and run the client. Your should see the following:

```
python client.py 
[12/27/25 09:45:02] INFO     Processing request of type ListToolsRequest                                                                                                                                                         
MCP Server tools
Tool:  add
Tool:  create_product
Using tool: create_product
Enter first value: silly
CALL TOOL
[12/27/25 09:45:08] INFO     Processing request of type CallToolRequest                                                                                                                                                          
[CLIENT] Received elicitation data: Are you sure you want to name your product as silly?
Sampling request: [SamplingMessage(role='user', content=TextContent(type='text', text='Create a product description about key-1, key-2', annotations=None, meta=None))]
[TextContent(type='text', text='{"id": "f44d224caf084065a8f5d76dfa3ae621", "name": "silly", "description": "This is a fake LLM response"}', annotations=None, meta=None)]

```

## Summary

Elicitation is the structured process by which a server or model explicitly requests missing information from a client when the available context is insufficient to proceed safely or correctly. In MCP, elicitation is a first-class interaction pattern defined by the protocol itself, rather than an informal follow-up question. MCP is designed for tool-using models, long-lived context, external memory, and multi-step reasoning, where guessing is not acceptable. As a result, execution is paused until the required information is provided. This approach improves correctness, safety, and user experience. When implementing elicitation, servers must avoid requesting sensitive information, clearly identify themselves, allow users to review or modify responses, respect privacy, and provide clear options to decline or cancel requests.

## References

1. Christoffer Noring _Learn Model Context Protocol with Python_, Packt

