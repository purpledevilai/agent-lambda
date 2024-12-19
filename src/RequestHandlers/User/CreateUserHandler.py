from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models.User import create_user, user_exists, User

def create_user_handler(lambda_event: LambdaEvent, user: CognitoUser) -> User:
    if user_exists(user.sub):
        raise Exception(f"User with id: {user.sub} already exists")
    return create_user(user.sub)
