# qubit-note: ReAct Implementation

Below, we shall implement a ReAct Agent in two ways:
● Manually executing each step for better clarity.
● Without manual intervention to fully automate the Reasoning and Action
process.

Let's look at the manual process first.
#1) ReAct with manual execution
In this section, we’ll implement a lightweight ReAct-style agent from scratch,
without using any orchestration framework like CrewAI or LangChain.
We'll manually simulate each round of the agent's reasoning, pausing, acting and
observing exactly as a ReAct loop is meant to function.
By running the logic cell-by-cell, we will gain full visibility and control over the
thinking process, allowing us to debug and validate the agent’s behavior at each
step.
To begin, we load the environment variables (like your LLM API key) and import
completion from LiteLLM (also install it first–pip install litellm), a lightweight
wrapper to query LLMs like OpenAI or local models via Ollama.

Next, we define a minimal Agent class, which wraps around a conversational
LLM and keeps track of its full message history - allowing it to reason
step-by-step, access system prompts, remember prior inputs and outputs, and
produce multi-turn interactions.

system (str): This is the system prompt that sets the personality and
behavioral constraints for the agent. If passed, it becomes the very first
message in the conversation just like in OpenAI Chat APIs.
● self.messages: This list acts as the conversation memory. Every interaction,
whether it’s user input or assistant output is appended to this list. This
history is crucial for LLMs to behave coherently across multiple turns.
● If system is provided, it's added to the message list using the special "role":
"system" identifier. This ensures that every completion that follows is
conditioned on the system instructions.
Next, we define a complete method in this class: