import json
from typing import Optional, Literal, Union
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from LLM.InteliSort import inteli_sort
from LLM.LLMExtract import llm_extract
from LLM.CreateLLM import create_llm
from Models.Job import get_job, save_job, JobStatus
from Models.TokenTracking import build_tracking_callback
from Models.LLMModel import validate_model_id
from Models.User import get_user


class InteliSortItem(BaseModel):
    id: str
    value: str

class InteliSortInput(BaseModel):
    items: list[Union[str, InteliSortItem]]
    prompt: str
    n: int
    model_id: Optional[str] = None

class ComparisonResult(BaseModel):
    """The victor of a comparison between two items."""
    victor: Literal["a", "b"]


def inteli_sort_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]):

    job = get_job(lambda_event.runJobId)
    job.status = JobStatus.in_progress
    job.message = "InteliSort in progress"
    save_job(job)

    # Parse and validate input
    body = InteliSortInput(**json.loads(lambda_event.body))

    if len(body.items) < 2:
        raise Exception("items must contain at least 2 elements", 400)
    if "ARG_ITEM_A" not in body.prompt or "ARG_ITEM_B" not in body.prompt:
        raise Exception("prompt must contain both ARG_ITEM_A and ARG_ITEM_B placeholders", 400)
    if body.n < 1:
        raise Exception("n must be a positive integer", 400)
    if body.n > len(body.items):
        raise Exception(f"n ({body.n}) cannot exceed the number of items ({len(body.items)})", 400)

    # Normalize items into {id, value} dicts
    items = []
    for i, item in enumerate(body.items):
        if isinstance(item, str):
            items.append({"id": str(i), "value": item})
        else:
            items.append({"id": item.id, "value": item.value})

    if body.model_id:
        validate_model_id(body.model_id)

    # Build comparison function backed by LLM
    llm = create_llm(body.model_id)

    tracking_callback = None
    if user:
        db_user = get_user(user.sub)
        if db_user.organizations:
            tracking_callback = build_tracking_callback(db_user.organizations[0])

    def compare(a, b):
        prompt = body.prompt.replace("ARG_ITEM_A", str(a["value"])).replace("ARG_ITEM_B", str(b["value"]))
        result = llm_extract(ComparisonResult, prompt, llm, on_response=tracking_callback)
        return a if result["victor"] == "a" else b

    # Build log function that persists progress to the Job
    def log(message):
        job.data["logs"] = job.data.get("logs", [])
        job.data["logs"].append(message)
        job.message = message
        save_job(job)

    # Run InteliSort
    sorted_items = inteli_sort(items, compare, body.n, log=log)

    # Store results and mark complete
    job.data["results"] = sorted_items
    job.status = JobStatus.completed
    job.message = f"InteliSort complete: top {body.n} selected"
    save_job(job)

    return job
