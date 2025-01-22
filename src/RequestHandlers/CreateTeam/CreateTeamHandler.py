import json
from AWS.Lambda import LambdaEvent, invoke_lambda
from AWS.Cognito import CognitoUser
from Models import Job, User
from typing import Optional
from pydantic import BaseModel


class LinkData(BaseModel):
    link: str  # Just in case we want to use it later
    data: str


class CreateTeamParams(BaseModel):
    org_id: Optional[str] = None
    business_name: str
    business_description: str
    link_data: list[LinkData]
    selected_members: list[str]


def create_team_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Job.Job:

    db_user = User.get_user(user.sub)

    # Get the body of the request
    body = CreateTeamParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = db_user.organizations[0]
    elif (body.org_id not in db_user.organizations):
        raise Exception("User does not have access to this organization", 403)

    # Create the job
    job = Job.create_job(
        owner_id=user.sub,
        data={
            agent_template_id: {
                "completed": False,
                "agent_id": None
            } for agent_template_id in body.selected_members
        },
        status=Job.JobStatus.in_progress
    )

    try: 
        # Send lambda event for each agent
        for agent_template_id in body.selected_members:
            invoke_lambda(
                lambda_name="create-agent-lambda",
                event={
                    "org_id": body.org_id,
                    "job_id": job.job_id,
                    "agent_template_id": agent_template_id,
                    "business_name": body.business_name,
                    "business_description": body.business_description,
                    "additional_link_info": ", ".join(link.data for link in body.link_data)
                }
            )
    except Exception as e:
        job.status = Job.JobStatus.error
        job.message = str(e)
        Job.save_job(job)

    return job
