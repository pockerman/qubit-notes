# qubit-note: Build a Local MCP Server & Client part 2

## Overview

In <a href="2025-08-27-build-local-mcp-server-and-client.md">qubit-note: Build a Local MCP Server & Client part 1</a> I discussed how to create a simple MCP
server and a client. In this qubit note I want to extend the server that we built in part by adding resources and prompts. I will also show how we can
test an MCP server using <a href="https://modelcontextprotocol.io/docs/tools/inspector">MCP Inspector</a>.

**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, Python


## Build a Local MCP Server & Client

Follow the instructions from <a href="2025-08-27-build-local-mcp-server-and-client.md">part 1</a> to install the requirements.
The new server implementation is shown below:

```
# server.py
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("Demo 🚀")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Addition tool. It adds two integers"""
    return a + b


@mcp.tool()
def multiply(first: int, second: int) -> int:
    """Mulitplication tool. It multiplies two numbers"""
    return first * second


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Resource. Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


if __name__ == "__main__":
    mcp.run()
```

We will use <a href="https://modelcontextprotocol.io/docs/tools/inspector">MCP Inspector</a> to test the server. This should be installed if you installed
the requirements for this part. Use

```
mcp dev server.py
```

This will open the MCP Inspector UI at http://localhost:6274 . Click connect to connect on the MCP server. On the UI you will be able to see the
resources, the tools and the prompts the server exposes. For example, clicking on the _Tools_ tab allows you to see the tools available on the server.
Click on list tools and you should be able to see the following response:

```
{
  "tools": [
    {
      "name": "add",
      "description": "Addition tool. It adds two integers",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": {
            "title": "A",
            "type": "integer"
          },
          "b": {
            "title": "B",
            "type": "integer"
          }
        },
        "required": [
          "a",
          "b"
        ],
        "title": "addArguments"
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "result": {
            "title": "Result",
            "type": "integer"
          }
        },
        "required": [
          "result"
        ],
        "title": "addOutput"
      }
    },
    {
      "name": "multiply",
      "description": "Mulitplication tool. It multiplies two numbers",
      "inputSchema": {
        "type": "object",
        "properties": {
          "first": {
            "title": "First",
            "type": "integer"
          },
          "second": {
            "title": "Second",
            "type": "integer"
          }
        },
        "required": [
          "first",
          "second"
        ],
        "title": "multiplyArguments"
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "result": {
            "title": "Result",
            "type": "integer"
          }
        },
        "required": [
          "result"
        ],
        "title": "multiplyOutput"
      }
    }
  ]
}
```

The MCP Inspector has two different modes, CLI mode and UI mode. We saw UI mode. The CLI mode can be used for for CI/CD scenarios.
Go the directory where the ```server.py``` file is located and run the following

```
npx @modelcontextprotocol/inspector --cli mcp run server.py --method tools/list
```

You should be able to see the same response as above. Note you will need Node.js installer for this.

## Summary

In this qubit-note we adde more capabilities to the MCP server we developed in <a href="2025-08-27-build-local-mcp-server-and-client.md">part 1</a>.
We also saw how how to use MCP Inspector in order to test the server.


## References

1. <a href="https://modelcontextprotocol.io/docs/tools/inspector">MCP Inspector</a>