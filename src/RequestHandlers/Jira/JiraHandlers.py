import json
import os
import time
import requests
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from AWS.CloudWatchLogs import get_logger
from Models import Integration, User
from Services import JiraService

logger = get_logger(log_level=os.environ.get("LOG_LEVEL", "INFO"))

JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
ACCESSIBLE_RESOURCES_URL = "https://api.atlassian.com/oauth/token/accessible-resources"


class JiraProxyResponse(BaseModel):
    data: dict


def jira_auth_code_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    body = json.loads(lambda_event.body)
    code = body.get("code")
    if not code:
        raise Exception("code is required", 400)

    db_user = User.get_user(user.sub)
    if len(db_user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    org_id = lambda_event.queryStringParameters.get("org_id") if lambda_event.queryStringParameters else None
    if not org_id:
        org_id = db_user.organizations[0]
    if org_id not in [org_id for org_id in db_user.organizations]:
        raise Exception("User is not a member of the specified organization", 403)

    payload = {
        "grant_type": "authorization_code",
        "client_id": os.environ["JIRA_CLIENT_ID"],
        "client_secret": os.environ["JIRA_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": os.environ["JIRA_REDIRECT_URI"],
    }
    resp = requests.post(JIRA_TOKEN_URL, json=payload)
    if resp.status_code != 200:
        raise Exception("Failed to exchange Jira auth code", resp.status_code)
    data = resp.json()

    integration_config = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data.get("expires_in"),
        "scope": data.get("scope"),
        "expires_at": int(time.time()) + data.get("expires_in", 0),
    }

    res = requests.get(
        ACCESSIBLE_RESOURCES_URL,
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    if res.status_code == 200:
        resources = res.json()
        if resources:
            integration_config["cloud_id"] = resources[0].get("id")
            integration_config["resource_url"] = resources[0].get("url")

    jira_integration = None
    for integ in Integration.get_integrations_in_org(org_id):
        if integ.type == "jira":
            jira_integration = integ
            break

    if jira_integration:
        jira_integration.integration_config = integration_config
        Integration.save_integration(jira_integration)
    else:
        jira_integration = Integration.create_integration(
            org_id=org_id, type="jira", integration_config=integration_config
        )

    return jira_integration


def jira_projects_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JiraProxyResponse:
    db_user = User.get_user(user.sub)
    data = JiraService.list_projects(db_user)
    return JiraProxyResponse(data=data)


def jira_create_issue_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JiraProxyResponse:
    db_user = User.get_user(user.sub)
    issue_data = json.loads(lambda_event.body)
    data = JiraService.create_issue(db_user, issue_data)
    return JiraProxyResponse(data=data)


def jira_get_issues_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JiraProxyResponse:
    db_user = User.get_user(user.sub)
    jql = None
    if lambda_event.queryStringParameters:
        jql = lambda_event.queryStringParameters.get("jql")
    data = JiraService.search_issues(db_user, jql=jql)
    return JiraProxyResponse(data=data)


def jira_update_issue_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JiraProxyResponse:
    db_user = User.get_user(user.sub)
    issue_id = lambda_event.requestParameters.get("issue_id")
    if not issue_id:
        raise Exception("issue_id is required", 400)
    body = json.loads(lambda_event.body)
    data = JiraService.update_issue(db_user, issue_id, body)
    return JiraProxyResponse(data=data)
