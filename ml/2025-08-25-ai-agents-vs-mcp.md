# qubit-note: AI Agent vs MCP

## Overview

In this qubit note, I go over some distinct differences between an AI agent and model context protocl or MCP (see <a href="2025-04-23-model-context-protocol.md">qubit-note: Model Context Protocol</a>).
This note is follows an article from <a href="https://bytebytego.com/">ByteByteGo</a>

**keywords** AI-engineering, AI-agents,  model-context-protocol, MCP

## AI Agent vs MCP

Software agents have been around for some time now. According to Wikipedia, <a href="https://en.wikipedia.org/wiki/Agent-oriented_programming">agent-oriented programming</a> 
 _...is a programming paradigm where the construction of the software is centered on the concept of software agents. In contrast to object-oriented programming which has objects (providing methods with variable parameters) at its core, AOP has externally specified agents (with interfaces and messaging capabilities) at its core. They can be thought of as abstractions of objects. Exchanged messages are interpreted by receiving "agents", in a way specific to its class of agents._

 Large language models have revolutionize the way we think software agents. An AI agent may gather data, analyse this data data in order to achieve goals.
 Thus the key aspects of contemorary agents are:

 - Autonomy: perform actions without a human in the loop
 - Memory: Agents can maintain short and long term memory. This allows an agent to better follow a discussion for example
 - Perception and analysis

AI agents implement in one way or another the sense-think-act cycle that it is very popular in the robotics community.

Model context protocol, or MCP, is a protocol,  introduced by Anthropic, that allows an agent to interact with databses, file systems or any other tooling that the agent may need.
MCP works as an enabling technology rather than an antagonistic one to AI agents.


## Summary

This note discusses the key differences between AI agents and the Model Context Protocol (MCP). AI agents, rooted in the concept of software agents, operate autonomously, utilize memory (both short and long term), and follow a sense-think-act cycle to analyze data and achieve goals. With advancements in large language models, their capabilities have significantly expanded. MCP, introduced by Anthropic, is a protocol designed to enable agents to interact with external systems such as databases, file systems, or tools. Rather than competing with AI agents, MCP serves as an enabling technology that enhances their ability to perform complex tasks by providing seamless access to external resources.


## References

1.  <a href="https://en.wikipedia.org/wiki/Agent-oriented_programming">Agent-oriented programming</a>
2. <a href="https://www.anthropic.com/news/model-context-protocol">Model context protocol</a>