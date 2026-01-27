from typing import List
from pydantic import BaseModel


class TerminatingConfig(BaseModel):
    tool_ids: List[str]
    consecutive_nudges: int = 1
    nudge_message: str = "You are currently in an autonomous execution mode with no user interaction. You must complete your task by calling one of the terminating tools."
    max_invocations: int = 64
