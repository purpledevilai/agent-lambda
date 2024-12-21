from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User

def create_user_handler(lambda_event: LambdaEvent, user: CognitoUser) -> User.User:
    if User.user_exists(user.sub):
        raise Exception(f"User with id: {user.sub} already exists")
    return User.create_user(user.sub)
