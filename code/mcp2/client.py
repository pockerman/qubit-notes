import asyncio
from mcp_use import MCPAgent, MCPClient
from langchain_ollama import ChatOllama


async def main() -> None:

    config = {
        "mcpServers":{
            "add":{
                "command": "python",
                "args": ["server.py"]
            }
        }
    }
    # create an MCP client
    client = MCPClient.from_dict(config)

    # create the agent. We need to pass an LLM
    llm = ChatOllama(model='llama3.2',
                     base_url="http://localhost:11434")

    agent = MCPAgent(llm=llm, client=client, max_steps=30)
    response = await agent.run("Add 1 and 2")
    print(response)


if __name__ == '__main__':
    asyncio.run(main())