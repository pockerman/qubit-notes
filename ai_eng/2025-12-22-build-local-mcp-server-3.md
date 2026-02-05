# qubit-note: Build an MCP Server Part 3

## Overview

In <a href="2025-08-27-build-local-mcp-server-and-client.md">qubit-note: Build an MCP Server part 1</a> I discussed how to create a simple MCP
server and a client.  In particular our server was using STDIO for transport.
In <a href="2025-12-21-build-local-mcp-server-and-client-2.md">qubit-note: Build an MCP Server part 2</a> we extended this server
using prompt templates and resources. We also saw how to use <a href="https://modelcontextprotocol.io/docs/tools/inspector">MCP Inspector</a> in order to
test our server. 

The servers both in part 1 and part 2 used STDIO for transport. This is a transport method for servers running locally.
In this qubit-note we use SSE. This is a transport method we can use if we want to connect to servers remotely via HTTP or if you want responses from LLMs streamed.
MCP supports various communication protocols, see https://fastmcp.mintlify.app/clients/transports. We will explore these later



**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, Python


## Build an MCP Server Part 3

Follow the instructions from <a href="2025-08-27-build-local-mcp-server-and-client.md">part 1</a> to install the requirements.
The new server implementation is shown below:

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


# or dynamically mount as host
#app.router.routes.append(Host('mcp.acme.corp', app=mcp.sse_app()))

```

We will need to expose our server as a web application. We use ```starlette``` for this. Open a terminal and type:

```
uvicorn server:app
```

You should see something like the following:

```
INFO:     Started server process [6735]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53716 - "GET /sse HTTP/1.1" 200 OK

```

By default the web server runs on port 8000 we can specify the port we want using ```--port 3000```.
We can access the exposed MCP server via a URL now; open a termnal and type: npx @modelcontextprotocol/inspector --cli http://localhost:8000/sse --method tools/list
You should see a response like the following:


```
{
  "tools": [
    {
      "name": "add",
      "description": "Tool to add two integer numbers",
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
    }
  ]
}
```

We can also use the UI of the MCP Inspector. Open a terminal and type:


```
mcp dev server.py
```

This will open the MCP Inspector UI at http://localhost:6274 .
We need to specify the URL of the web server that runs our MCP server that is: http://127.0.0.1:8000 then click connect and you should
be able to access the tool exposed by the server.




## Summary

In this qubit-note we continue building an MCP server. In earlier parts, the server used STDIO, suitable only for local transport. This part introduces Server-Sent Events (SSE) to allow remote or streaming communication over HTTP. 

SSE is somehow considered deprecated and the main transport for communicating over HTTP with MCP serveres is Streamable HTTP. 
We will cover this in <a href="2025-12-22-build-local-mcp-server-4.md">part 4</a>.

## References

1. <a href="https://fastmcp.mintlify.app/clients/transports">Client Transports</a>