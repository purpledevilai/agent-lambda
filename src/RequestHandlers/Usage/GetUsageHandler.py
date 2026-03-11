import time
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
from collections import defaultdict
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models.User import get_user
from Models.TokenTracking import get_token_trackings_for_org
from Models.LLMModel import get_model_or_none

logger = logging.getLogger(__name__)


class DailyUsage(BaseModel):
    date: str
    total_tokens: int

class ModelCost(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    cost: str

class UsageResponse(BaseModel):
    daily_usage: list[DailyUsage]
    total_cost: str
    model_costs: list[ModelCost]


def get_usage_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> UsageResponse:
    t0 = time.time()

    params = lambda_event.queryStringParameters or {}
    start_date_str = params.get("start_date")
    end_date_str = params.get("end_date")
    timezone_str = params.get("timezone", "UTC")

    logger.info(f"[usage] start_date={start_date_str} end_date={end_date_str} tz={timezone_str} user={user.sub}")

    if not start_date_str or not end_date_str:
        raise Exception("start_date and end_date query parameters are required", 400)

    try:
        tz = ZoneInfo(timezone_str)
    except Exception:
        raise Exception(f"Invalid timezone: {timezone_str}", 400)

    # Parse date strings (YYYY-MM-DD) into timezone-aware start/end timestamps
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=tz)
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=tz) + timedelta(days=1)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    # Get the user's org
    t1 = time.time()
    db_user = get_user(user.sub)
    logger.info(f"[usage] get_user took {time.time() - t1:.2f}s")

    if not db_user.organizations:
        raise Exception("User does not belong to any organization", 400)

    requested_org_id = params.get("org_id")
    if requested_org_id:
        if requested_org_id not in db_user.organizations:
            raise Exception("User does not belong to the specified organization", 403)
        org_id = requested_org_id
    else:
        org_id = db_user.organizations[0]

    logger.info(f"[usage] org_id={org_id} range={start_ts}-{end_ts}")

    # Query token trackings for the org in the time range
    t2 = time.time()
    trackings = get_token_trackings_for_org(org_id, start_ts, end_ts)
    logger.info(f"[usage] get_token_trackings_for_org took {time.time() - t2:.2f}s, returned {len(trackings)} records")

    # Group by day (in the requested timezone) for bar chart
    daily_tokens = defaultdict(int)
    for t in trackings:
        day_str = datetime.fromtimestamp(t.created_at, tz=tz).strftime("%Y-%m-%d")
        daily_tokens[day_str] += t.input_tokens + t.output_tokens

    # Build sorted daily usage list (fill gaps so every day in range is present)
    daily_usage = []
    current_day = start_dt
    while current_day < end_dt:
        day_str = current_day.strftime("%Y-%m-%d")
        daily_usage.append(DailyUsage(date=day_str, total_tokens=daily_tokens.get(day_str, 0)))
        current_day += timedelta(days=1)

    # Group by model for cost calculation
    model_totals: dict[str, dict] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0})
    for t in trackings:
        model_totals[t.model]["input_tokens"] += t.input_tokens
        model_totals[t.model]["output_tokens"] += t.output_tokens

    # Calculate costs per model
    t3 = time.time()
    model_costs = []
    total_cost = 0.0
    for model_name, totals in model_totals.items():
        llm_model = get_model_or_none(model_name)
        if llm_model:
            input_cost = (totals["input_tokens"] / 1_000_000) * llm_model.input_token_cost
            output_cost = (totals["output_tokens"] / 1_000_000) * llm_model.output_token_cost
            cost = input_cost + output_cost
        else:
            cost = 0.0

        model_costs.append(ModelCost(
            model=model_name,
            input_tokens=totals["input_tokens"],
            output_tokens=totals["output_tokens"],
            cost=f"${cost:,.2f} USD",
        ))
        total_cost += cost
    logger.info(f"[usage] cost calculation took {time.time() - t3:.2f}s for {len(model_totals)} models")

    logger.info(f"[usage] total handler time {time.time() - t0:.2f}s")

    return UsageResponse(
        daily_usage=daily_usage,
        total_cost=f"${total_cost:,.2f} USD",
        model_costs=model_costs,
    )
