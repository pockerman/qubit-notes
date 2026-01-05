# qubit-note: AI Series | Build an MCP Server Part 1

## Overview

The Model Context Protocol (MCP) is an architectural pattern and open standard designed to enable AI agents, such as large language models (LLMs), to access and interact with external tools, data sources, and repositories in a unified, standardized way, see also <a href="ml/2025-04-23-model-context-protocol.md">qubit-note: Model Context Protocol</a> . It was introduced by Anthropic in late 2024 to solve a growing challenge: AI agents need to integrate with diverse and often complex systems (databases, APIs, file systems, search engines), but traditional methods involve fragmented, bespoke integrations that are hard to scale and maintain. 

In this qubit note we will see how to build an MCP server using <a href="https://gofastmcp.com/getting-started/welcome">FastMCP</a> and a client using <a href="https://github.com/mcp-use/mcp-use">mcp-use</a>, <a href="https://github.com/ollama/ollama">Ollama</a> and Python. We will use a rather trivial example in this note as I simply want to illustrate the approach.

**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, Python

## Build an MCP Server Part 1

Let's first create a new environment in our system. I am using Anaconda for this but any other tool will do the trick.
With Ananconda, simply execute:

```
conda create -n mcp-exe-3.12 python=3.12
```

Activate the environment with:

```
conda activate mcp-exe-3.12
```


Install, the requirements. I am using <a href="https://github.com/astral-sh/uv">uv</a> as a package manager so I need to install this:

```
pip install uv
```

then install the requirements with:

```
uv pip install -r requirements.txt
```

We will be using Ollama as our LLM provider but feel free to use anything else. I already have Ollama installed in my machine.
Start the Ollama server using

```
OLLAMA_HOST=0.0.0.0 OLLAMA_PORT=11434 ollama serve
``` 

We will be using ```llama3.2```. If not already pulled into your local Ollama server, open another terminal and use the following to do so:

```
curl http://localhost:11434/api/pull -d '{
  "model": "llama3.2"
}'
```

### Create the MCP server

Let's first create the MCP server. We will use <a href="https://gofastmcp.com/getting-started/welcome">FastMCP</a>. 
The following snipper create a simple MCP server that only exposes an ```add``` endpoint:

```
# server.py

from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

You can now run this, by opening a terminal, activating the environment we specified above and run:

```
python server.py
```

However, we won't use the server as a long running process. Instead we will use the default stdion transport. 


----
**Remark**

MCP servers and client communicate using different protocols. FastMCP supports three main transport protocols, each designed for specific use cases and deployment scenarios.
The default transport protocol is STDIO. In this approach, the client spawns a new server process for each session and manages its lifecycle. The server reads MCP messages from stdin and writes responses to stdout. This is why STDIO servers don’t stay running - they’re started on-demand by the client.

Check the FastAPI documentation about the supported <a herf="https://gofastmcp.com/deployment/running-server">Transport Protocols</a>


---- 

### Creating the client

We will use <a href="https://github.com/mcp-use/mcp-use">mcp-use</a> in order to create our agent. The following snippet shows how to:

```
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
```

Notice how we instruct the client to satrt the server. Open a terminal, activate the environment and run the script:

```
python client.py
```

This should produce something similar to: 

```
2025-08-27 08:22:01,933 - mcp_use.telemetry.telemetry - INFO - Anonymized telemetry enabled. Set MCP_USE_ANONYMIZED_TELEMETRY=false to disable.
2025-08-27 08:22:01,934 - mcp_use - INFO - 🚀 Initializing MCP agent and connecting to services...
2025-08-27 08:22:01,934 - mcp_use - INFO - 🔌 Found 0 existing sessions
2025-08-27 08:22:01,934 - mcp_use - INFO - 🔄 No active sessions found, creating new ones...


╭─ FastMCP 2.0 ──────────────────────────────────────────────────────────────╮
│                                                                            │
│        _ __ ___ ______           __  __  _____________    ____    ____     │
│       _ __ ___ / ____/___ ______/ /_/  |/  / ____/ __ \  |___ \  / __ \    │
│      _ __ ___ / /_  / __ `/ ___/ __/ /|_/ / /   / /_/ /  ___/ / / / / /    │
│     _ __ ___ / __/ / /_/ (__  ) /_/ /  / / /___/ ____/  /  __/_/ /_/ /     │
│    _ __ ___ /_/    \__,_/____/\__/_/  /_/\____/_/      /_____(_)____/      │
│                                                                            │
│                                                                            │
│                                                                            │
│    🖥️  Server name:     Demo 🚀                                             │
│    📦 Transport:       STDIO                                               │
│                                                                            │
│    📚 Docs:            https://gofastmcp.com                               │
│    🚀 Deploy:          https://fastmcp.cloud                               │
│                                                                            │
│    🏎️  FastMCP version: 2.11.3                                              │
│    🤝 MCP version:     1.13.1                                              │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯


[08/27/25 08:22:02] INFO     Starting MCP server 'Demo 🚀' with transport 'stdio'                                                                                                                                               server.py:1445
2025-08-27 08:22:02,364 - mcp_use - INFO - ✅ Created 1 new sessions
2025-08-27 08:22:02,368 - mcp_use - INFO - 🛠️ Created 1 LangChain tools from client
2025-08-27 08:22:02,368 - mcp_use - INFO - 🧰 Found 1 tools across all connectors
2025-08-27 08:22:02,369 - mcp_use - INFO - 🧠 Agent ready with tools: add
2025-08-27 08:22:02,371 - mcp_use - INFO - ✨ Agent initialization complete
2025-08-27 08:22:02,371 - mcp_use - INFO - 💬 Received query: 'Add 1 and 2'
2025-08-27 08:22:02,371 - mcp_use - INFO - 🏁 Starting agent execution with max_steps=30
2025-08-27 08:22:02,371 - mcp_use - INFO - 👣 Step 1/30
2025-08-27 08:22:05,189 - mcp_use - INFO - 💭 Reasoning:  Invoking: `add` with `{'a': '1', 'b': '2'}`   
2025-08-27 08:22:05,189 - mcp_use - INFO - 🔧 Tool call: add with input: {'a': '1', 'b': '2'}
2025-08-27 08:22:05,189 - mcp_use - INFO - 📄 Tool result: 3
2025-08-27 08:22:05,189 - mcp_use - INFO - 💭 Reasoning:  Invoking: `add` with `{'a': '1', 'b': '2'}`   
2025-08-27 08:22:05,189 - mcp_use - INFO - 🔧 Tool call: add with input: {'a': '1', 'b': '2'}
2025-08-27 08:22:05,189 - mcp_use - INFO - 📄 Tool result: 3
2025-08-27 08:22:05,189 - mcp_use - INFO - 👣 Step 2/30
2025-08-27 08:22:05,773 - mcp_use - INFO - ✅ Agent finished at step 2
2025-08-27 08:22:05,773 - mcp_use - INFO - 🎉 Agent execution complete in 3.8389060497283936 seconds
Thought: I now know the final answer
Final Answer: The final answer to the original question is 3.

```


Notice, the rather long duration the agent needed to complete a rather trivial task.

## Summary

This qubit note showcased how to create an MCP server using FastMCP and a client using mcp-use. We used the default transport protocol from FastMCP i.e. STDIO whereby the
client creates and manages the MCP server. This approach is ideal for local development and experimentaiton but may not be appropriate for production.
The overall agent execution took almost 4 seconds for a rather trivial task. In addition, albeit MCP benefits are undeniable, we do end up with a system probabbly more complex.

## References

1. <a href="https://gofastmcp.com/getting-started/welcome">FastMCP</a>
2. <a href="https://github.com/mcp-use/mcp-use">mcp-use</a>
3. <a href="https://github.com/astral-sh/uv">uv</a>

