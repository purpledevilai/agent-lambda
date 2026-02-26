from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models.LLMModel import get_all_models, LLMModel


def get_models_handler(lambda_event: LambdaEvent, user: CognitoUser) -> list[LLMModel]:
    return get_all_models()
