import boto3

# Get user from cognito
def get_user_from_cognito(access_token):
    cognito = boto3.client("cognito-idp")
    response = cognito.get_user(
        AccessToken=access_token
    )
    user_attributes = response['UserAttributes']
    user = {attr['Name']: attr['Value'] for attr in user_attributes}
    return user