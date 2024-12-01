from pydantic import Field, BaseModel
from LLM.AgentChat import AgentTool

class setPrompt(BaseModel):
  prompt: str = Field(description="The draft or version of the prompt")

def set_prompt(prompt: str, context: dict) -> str:
  if "ui_updates" not in context:
    context["ui_updates"] = []
  context["ui_updates"].append({
    "type": "set_prompt",
    "prompt": prompt
  })
  return f"Prompt set!"

set_prompt_tool = AgentTool(function=set_prompt, params=setPrompt, pass_context=True)