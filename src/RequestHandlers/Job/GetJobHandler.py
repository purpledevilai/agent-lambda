from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Job

def get_job_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Job.Job:
    # Get the path parameters
    job_id = lambda_event.requestParameters.get("job_id")
    if ( not job_id):
        raise Exception("job_id is required", 400)
    job = Job.get_job_for_owner(job_id, user.sub)
    return job