from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models.LLMModel import get_all_models, LLMModel
from pydantic import BaseModel



class GetModelsResponse(BaseModel):
    models: list[LLMModel]

def get_models_handler(lambda_event: LambdaEvent, user: CognitoUser) -> list[LLMModel]:
    return GetModelsResponse(models=get_all_models())
