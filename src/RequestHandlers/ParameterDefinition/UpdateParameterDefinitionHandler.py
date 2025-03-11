import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ParameterDefinition, User

def update_parameter_definition_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ParameterDefinition.ParameterDefinition:   
    
    # Get the body of the request
    body = ParameterDefinition.UpdateParameterDefinitionParams(**json.loads(lambda_event.body))

    # Get the parameter_definition
    pd_id = lambda_event.requestParameters.get("pd_id")
    if (not pd_id):
        raise Exception("pd_id is required", 400)
    
    # Get the user
    dbUser = User.get_user(user.sub)

    # Get the parameter_definition
    parameter_definition = ParameterDefinition.get_parameter_definition_for_user(pd_id, dbUser)

    # Update the parameter_definition
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    parameter_definition_dict = parameter_definition.model_dump()
    parameter_definition_dict.update(update_dict)
    update_parameter_definition = ParameterDefinition.ParameterDefinition(**parameter_definition_dict)

    ParameterDefinition.save_parameter_definition(update_parameter_definition)

    return update_parameter_definition


    


            