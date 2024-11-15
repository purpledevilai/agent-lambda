from typing import List, Tuple, Callable, Any
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage

class AgentChat:
  def __init__(
      self,
      llm: BaseChatModel,
      prompt: str,
      tools: List[Tuple[BaseModel, Callable[[Any], str]]] = None,
      messages: List[BaseMessage] = []
  ):
    self.messages = messages
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt),
        (MessagesPlaceholder(variable_name="messages"))
    ])
    if tools:
      tool_params_list = []
      self.name_to_tool = {}
      for tool_params, tool in tools:
        tool_params_list.append(tool_params)
        self.name_to_tool[tool_params.__name__] = tool
      llm = llm.bind_tools(tool_params_list)
    self.prompt_chain = prompt | llm

  def invoke(self):
    response = self.prompt_chain.invoke({"messages": self.messages})
    self.messages.append(response)
    if len(response.tool_calls) > 0:
      for tool_call in response.tool_calls:
        try:
          tool_response = self.name_to_tool[tool_call["name"]](**tool_call['args'])
          tool_message = ToolMessage(tool_call_id=tool_call['id'], content=tool_response)
        except Exception as e:
          tool_message = ToolMessage(tool_call_id=tool_call['id'], content=f"Issue calling tool: {tool_call['name']}, error: {e}")
        self.messages.append(tool_message)
      return self.invoke()
    return response.content

  def add_human_message_and_invoke(self, message: str):
    self.messages.append(HumanMessage(content=message))
    return self.invoke()