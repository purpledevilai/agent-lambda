import os
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from AWS.DynamoDB import query_by_pk_and_sk_range
from Models.User import get_user
from Models.TokenTracking import get_token_trackings_for_org
from Models.LLMModel import get_model_or_none

logger = logging.getLogger(__name__)

DAILY_USAGE_TABLE_NAME = os.environ["DAILY_USAGE_TABLE_NAME"]

UTC = timezone.utc


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

    logger.info(f"[usage] start_date={start_date_str} end_date={end_date_str} user={user.sub}")

    if not start_date_str or not end_date_str:
        raise Exception("start_date and end_date query parameters are required", 400)

    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=UTC)
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=UTC) + timedelta(days=1)

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

    logger.info(f"[usage] org_id={org_id}")

    today_utc = datetime.now(UTC).strftime("%Y-%m-%d")

    # ── 1. Query daily_usage for aggregated past days ──
    t2 = time.time()
    agg_items = query_by_pk_and_sk_range(
        table_name=DAILY_USAGE_TABLE_NAME,
        partition_key="org_id",
        partition_value=org_id,
        sort_key="date",
        sort_min=start_date_str,
        sort_max=end_date_str,
    )
    logger.info(f"[usage] daily_usage query took {time.time() - t2:.2f}s, returned {len(agg_items)} days")

    daily_tokens: dict[str, int] = defaultdict(int)
    model_totals: dict[str, dict] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0})

    for item in agg_items:
        date_str = item["date"]
        daily_tokens[date_str] += int(item.get("total_input_tokens", 0)) + int(item.get("total_output_tokens", 0))

        models_map = item.get("models", {})
        for model_name, model_data in models_map.items():
            inp = int(model_data.get("input_tokens", 0))
            out = int(model_data.get("output_tokens", 0))
            model_totals[model_name]["input_tokens"] += inp
            model_totals[model_name]["output_tokens"] += out

    # ── 2. Query today's raw token_tracking records (small, fast) ──
    if start_date_str <= today_utc <= end_date_str:
        today_start_ts = int(datetime.strptime(today_utc, "%Y-%m-%d").replace(tzinfo=UTC).timestamp())
        today_end_ts = today_start_ts + 86400

        t3 = time.time()
        today_trackings = get_token_trackings_for_org(org_id, today_start_ts, today_end_ts)
        logger.info(f"[usage] today's token_tracking query took {time.time() - t3:.2f}s, returned {len(today_trackings)} records")

        for t_rec in today_trackings:
            daily_tokens[today_utc] += t_rec.input_tokens + t_rec.output_tokens
            model_totals[t_rec.model]["input_tokens"] += t_rec.input_tokens
            model_totals[t_rec.model]["output_tokens"] += t_rec.output_tokens

    # ── 3. Build sorted daily usage list (fill gaps) ──
    daily_usage = []
    current_day = start_dt
    while current_day < end_dt:
        day_str = current_day.strftime("%Y-%m-%d")
        daily_usage.append(DailyUsage(date=day_str, total_tokens=daily_tokens.get(day_str, 0)))
        current_day += timedelta(days=1)

    # ── 4. Calculate costs per model ──
    t4 = time.time()
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
    logger.info(f"[usage] cost calculation took {time.time() - t4:.2f}s for {len(model_totals)} models")

    logger.info(f"[usage] total handler time {time.time() - t0:.2f}s")

    return UsageResponse(
        daily_usage=daily_usage,
        total_cost=f"${total_cost:,.2f} USD",
        model_costs=model_costs,
    )
