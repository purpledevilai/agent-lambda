import os
import uuid
from datetime import datetime
from AWS.DynamoDB import put_item, get_items_by_index_range
from pydantic import BaseModel

TOKEN_TRACKING_TABLE_NAME = os.environ["TOKEN_TRACKING_TABLE_NAME"]

class TokenTracking(BaseModel):
    tracking_id: str
    org_id: str
    model: str
    input_tokens: int
    output_tokens: int
    created_at: int

class InvocationTokenTracker:
    """Accumulates token usage across all LLM calls in a single invocation and persists each to DynamoDB."""
    def __init__(self, org_id: str, model_id: str = None):
        self.org_id = org_id
        self.model_id = model_id
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def on_response(self, response):
        usage = getattr(response, 'usage_metadata', None)
        if usage:
            model_name = self.model_id or getattr(response, 'response_metadata', {}).get('model_name', 'unknown')
            input_tokens = usage.get('input_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'output_tokens', 0)
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            create_token_tracking(
                org_id=self.org_id,
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

    def calculate_cost(self, input_token_cost: float, output_token_cost: float) -> float:
        """Calculate total invocation cost from per-million token prices."""
        input_cost = (self.total_input_tokens * input_token_cost) / 1_000_000
        output_cost = (self.total_output_tokens * output_token_cost) / 1_000_000
        return round(input_cost + output_cost, 10)


def build_tracking_callback(org_id: str, model_id: str = None):
    """Returns an on_response callback that saves token tracking for the given org."""
    tracker = InvocationTokenTracker(org_id, model_id)
    return tracker.on_response

def get_token_trackings_for_org(org_id: str, start_time: int, end_time: int) -> list[TokenTracking]:
    """Query all token tracking records for an org within a unix-timestamp range."""
    items = get_items_by_index_range(
        table_name=TOKEN_TRACKING_TABLE_NAME,
        index_name="org_id-created_at-index",
        partition_key="org_id",
        partition_value=org_id,
        sort_key="created_at",
        sort_min=start_time,
        sort_max=end_time,
        projection_expression="model, input_tokens, output_tokens, created_at",
    )
    return [TokenTracking(tracking_id="", org_id=org_id, **item) for item in items]

def create_token_tracking(org_id: str, model: str, input_tokens: int, output_tokens: int) -> TokenTracking:
    data = {
        "tracking_id": str(uuid.uuid4()),
        "org_id": org_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "created_at": int(datetime.timestamp(datetime.now())),
    }
    token_tracking = TokenTracking(**data)
    put_item(TOKEN_TRACKING_TABLE_NAME, data)
    return token_tracking
