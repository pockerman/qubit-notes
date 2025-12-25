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
