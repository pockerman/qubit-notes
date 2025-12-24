# qubit-note: Build an MCP Server Part 4


## Overview

In <a href="2025-12-22-build-local-mcp-server-part-3.md">qubit-note: Build an MCP Server Part 3</a> I discussed how to create a simple MCP
server that uses SSE for transport. This is a transport method we can use if we want to connect to servers remotely via HTTP or if you want responses from LLMs streamed.
However, SSE is slowly becoming deprecated and the prefered transport method now is Streamable HTTP.

In this quibit-note we will dicsuss how to implement Streamable HTTP for our MCP server.


**keywords:** programming, AI-engineering, AI-architecture, Model-Context-Protocol, MCP, Python

## Build an MCP Server Part 4

Before we see who to implement Streamable MCP, let's discuss some of the advanatges it offers, see also [1].
This transport method offers two advanatges when compared to SSE

- Resumability
- Bidirectional communication

Resumability allows clients to reliably resume interrupted streams by using headers like Last-Event-ID and Mcp-Session-ID, so if a connection drops, the client can reconnect and continue receiving data from where it left off instead of restarting the stream.  Streamable HTTP can support bidirectional communication and therefore is more versatile for agent-to-agent or client-server interactions.

In addition, Streamable HTTP allows clients and servers to communicate over a single endpoint that supports both POST and GET methods.
It also aligns with the  evolving MCP standards and best practices. It’s modular, extensible, and designed for stateless or session-based models. 
Stateless servers are more lightweight and easier to construct, and being able to choose the right model for the right scenario is a compelling argument [1].
It also aligns better with HTTP infrastructure i.e. proxies, API gateways and load balancers than SSE.

----
**Remark**

In MCP, streaming isn’t about chunking files or partial AI responses, but about transmitting data over HTTP using the Streamable HTTP standard, where clients indicate support by sending an 
```Accept: application/json, text/event-stream``` header.

----

Let's see how to create an MCP server using Streamable HTTP. The following code, taken from [1], shows how to

```
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, AsyncGenerator
from mcp.types import (
    LoggingMessageNotificationParams,
    TextContent
)


# Create an MCP server
mcp = FastMCP("Streamable DEMO")

# Add tool
@mcp.tool(description="A simple tool returning file content")
async def echo(message: str, ctx: Context) -> str:
    await ctx.info(f"Processing file 1/3:")
    await ctx.info(f"Processing file 2/3:")
    await ctx.info(f"Processing file 3/3:")
    return f"Here's the file content: {message}"

# Set up the transport as streamable HTTP.
mcp.run(transport="streamable-http")
```

We can run the server using

```
mcp dev server.py
```

In the previous parts we used MCP Inspector to test the server. We can also use ```cURL``` to do so:

```
curl -X POST "http://127.0.0.1:8000/mcp" -H "Accept: text/event-stream, application/json" -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": { "protocolVersion": "2025-03-26", "capabilities": { "tools": {} }, "clientInfo": { "name": "ExampleClient", "version": "1.0.0" } }
}'

``` 

The response should be: 

```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"Streamable DEMO","version":"1.13.1"}}}

```       

## Summary

This qubit-note introduces Streamable HTTP as the preferred transport for MCP servers, replacing SSE. It explains that Streamable HTTP offers key advantages such as resumable streams (via headers like Last-Event-ID and Mcp-Session-ID), bidirectional communication, and better compatibility with modern HTTP infrastructure like proxies and load balancers. Unlike traditional ideas of streaming, MCP streaming focuses on how data is transmitted over HTTP using the Streamable standard, indicated by the ```Accept: application/json, text/event-stream``` header. The post demonstrates how to implement a Streamable HTTP MCP server in Python  and illustrates how to test it using ```curl```.

## References

1. Christoffer Noring _Learn Model Context Protocol with Python_, Packt
2. <a href="https://dev.to/yigit-konur/understanding-streamable-http-the-new-one-after-sse-of-mcp-serverclient-architecture-vs-sse-3hfj">Understanding Streamable HTTP (the new one after SSE) of MCP Server/Client Architecture (+vs SSE)</a>