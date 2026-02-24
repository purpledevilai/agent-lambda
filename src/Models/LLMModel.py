import os
from AWS.DynamoDB import get_item, put_item
from pydantic import BaseModel

MODELS_TABLE_NAME = os.environ["MODELS_TABLE_NAME"]
MODELS_PRIMARY_KEY = "model"

class LLMModel(BaseModel):
    model: str
    input_token_cost: float
    output_token_cost: float

def get_model(model_name: str) -> LLMModel:
    item = get_item(MODELS_TABLE_NAME, MODELS_PRIMARY_KEY, model_name)
    if item is None:
        raise Exception(f"Model '{model_name}' not found in models table")
    return LLMModel(**item)

def get_model_or_none(model_name: str) -> LLMModel | None:
    item = get_item(MODELS_TABLE_NAME, MODELS_PRIMARY_KEY, model_name)
    if item is None:
        return None
    return LLMModel(**item)
