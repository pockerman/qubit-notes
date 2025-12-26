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
