from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages
from Models import Context, Agent
from Tools.ToolRegistry import tool_registry

def invoke_context(context: Context.Context, agent: Agent.Agent) -> Context.Context:
    agentChat: AgentChat = AgentChat(
        create_llm(),
        agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=[tool_registry[tool.name] for tool in agent.tools] if agent.tools else [],
        context=context.model_dump()
    )
    agentChat.invoke()

    # Save the new message to context
    context.messages = base_messages_to_dict_messages(agentChat.messages)
    Context.save_context(context)

    return context