# Note: Model Context Protocol

In this note, I give a high level overview of the <a href="https://www.anthropic.com/news/model-context-protocol">model context protocol</a> paradigm or MCP
for short. Then I would like to cover the MCP architecture from a rather hight level perspective.

**keywords** model-context-protocol, ai-agents, large-language-models

## Model Context Protocol

Let' frist try to understand what MCP really is. The MCP standard was introduced by <a href="https://www.anthropic.com/">ANTHROPIC</a>
in November 2024. The standard allows AI agents (e.g. LLMs) to connect to various tools, data sources and repositories that they
might need in order to execute their task. The MCP standard aims at hidding the complexity that is needed in order to have an agent being able to have 
access to a specific data source. Indeed, according to ANTHROPIC:

_... It provides a universal, open standard for connecting AI systems with data sources, replacing fragmented integrations with a single protocol. 
The result is a simpler, more reliable way to give AI systems access to the data they need._

The following figure illustrates the idea behind MCP.

| ![orchestrator-vs-choreography](./imgs/mcp_schematics.png)  |
|:-----------------------------------------------------------:|
|             **Figure 1: MCP schematics**                    |

The idea is akin to the <a href="https://microservices.io/patterns/apigateway.html">API Gateway pattern</a> from the client perspecitve.

So how this whole thing works then? The idea is rather simple, which is what makes it really great;
AI engineers can either expose their resources using an MCP server or can develop AI agents (or according to the article above MCP clients)
that connect to these MCP servers. 

One thing one must appreciate is that MCP does not add anything new in an agent per ce but rather allows to more easilly integrate
functionality that our agent may require.


### MCP Architecture

Now that we have an understanding what MCP is let's turn into the architecture of the protocol.
First you should note that MCP follows a <a href="https://en.wikipedia.org/wiki/Client%E2%80%93server_model">client-server architecture paradigm</a>.
However, each server focuses on a specific domain e.g. seraching over the internet or various database operations. in addition, it includes the following actors:

- MCP client
- MCP host
- MCP server

As mentioned above, an  MCP server exposes specific actions, perhaps around one domain, that an MCP client can access. 
An MCP client is hosted by an MCP host. Note that the MCP client can connect to multiple MCP servers.




## References

1. <a href="https://www.anthropic.com/news/model-context-protocol">model context protocol</a>
2. <a href="https://microservices.io/patterns/apigateway.html">API Gateway pattern</a>
2. <a href="https://www.youtube.com/watch?v=5xqFjh56AwM">MCP Crash Course for Python Developers</a>
