# qubit-note: qubit-note: AI Series | Build an MCP Client

## Overview 

Qubit note <a href="how_to/2025-08-27-build-local-mcp-server-and-client.md">qubit-note: Build an MCP Server Part 1</a> showed how to build an MCP server
that uses STDIO for transport. We extended this in 
<a href="how_to/2025-12-22-build-local-mcp-server-3.md">part 3</a> and <a href="how_to/2025-12-22-build-local-mcp-server-4.md">part 4</a>
looking into SSE and Streamable HTTP. We implemented in part 1 an MCP client as well.

In this qubit-note we will go more into the details of an MCP client.


**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, MCP-client, Python

## qubit-note: Build an MCP Client

To consume an MCP server, you need some form of client. You could, for example, use an application such as Claude Desktop or Virtual Studio Code (VS Code), as they have the ability to consume MCP servers and will handle the discovery of features and be able to use them. There are also cases where you want your own written client. A good example of this situation is when you want to build in AI capabilities as part of your app. Imagine, for example, that you have an e-commerce app and want to have an AI-improved search. The MCP server would be a separate app, whereas the client would be built into the e-commerce app.

The following code shows how to implement an MCP client that list the resources and tools available on an MCP server.
The MCP client code in this example is edited from [1].

```
# client.py
from typing import Any
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for STDIO connection
server_params = StdioServerParameters(
    command="mcp",  # Executable
    args=["run", "server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
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




async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the connection
            await session.initialize()

            # list resources
            await list_resources(session)

            # list tools
            tools = await list_tools(session)

            tool_name = tools.tools[0].name
            print(f"Using tool: {tool_name}")
            first_value = input("Enter first value: ")
            second_value = input("Enter second value: ")

            await call_tool(tool_name=tools.tools[0].name, 
                            session=session, **{"a": first_value, "b": second_value})

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

The MCP server is shown below

```
# server.py
from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo 🚀")

# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Tool to add two integer numbers"""
    return a + b
```

Execute the MCP client as Python script: ```python client.py```. You should see the following

```
[12/25/25 09:17:34] INFO     Processing request of type ListResourcesRequest                                                                                                                                                     
MCP Server resources
Resource:  ('meta', None)
Resource:  ('nextCursor', None)
Resource:  ('resources', [])
                    INFO     Processing request of type ListToolsRequest                                                                                                                                                        
MCP Server tools
Tool:  add
Using tool: add
Enter first value: 1
Enter second value: 2
CALL TOOL
[12/25/25 09:17:38] INFO     Processing request of type CallToolRequest                                                                                                                                                          
[TextContent(type='text', text='3', annotations=None, meta=None)]

```

## Summary

This qubit-note discussed how to create an MCP client that queries an MCP server about tools and resources. We also saw how
to use the tools available on the server. 

## References

1. <a her="https://modelcontextprotocol.io/docs/develop/build-client">Build an MCP client</a>
2. 1. Christoffer Noring _Learn Model Context Protocol with Python_, Packt


