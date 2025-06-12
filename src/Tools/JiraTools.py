from pydantic import BaseModel, Field
from LLM.AgentChat import AgentTool
from Models import User
from Services import JiraService
import json


class JiraCreateIssueParams(BaseModel):
    project_key: str = Field(description="Key of the Jira project")
    summary: str = Field(description="Issue summary")
    description: str = Field(description="Issue description")
    issue_type: str = Field(default="Task", description="Type of the issue")


def jira_create_issue_func(project_key: str, summary: str, description: str, issue_type: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        }
        res = JiraService.create_issue(user, issue_data)
        return json.dumps(res)
    except Exception as e:
        return f"Error creating issue: {e}"


jira_create_issue_tool = AgentTool(params=JiraCreateIssueParams, function=jira_create_issue_func, pass_context=True)


class JiraSearchIssuesParams(BaseModel):
    jql: str = Field(description="Jira Query Language string to search issues")


def jira_search_issues_func(jql: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.search_issues(user, jql=jql)
        return json.dumps(res)
    except Exception as e:
        return f"Error searching issues: {e}"


jira_search_issues_tool = AgentTool(params=JiraSearchIssuesParams, function=jira_search_issues_func, pass_context=True)


class JiraUpdateIssueParams(BaseModel):
    issue_id: str = Field(description="ID or key of the issue to update")
    summary: str | None = Field(default=None, description="Updated summary")
    description: str | None = Field(default=None, description="Updated description")


def jira_update_issue_func(issue_id: str, summary: str | None, description: str | None, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        fields = {}
        if summary is not None:
            fields["summary"] = summary
        if description is not None:
            fields["description"] = description
        data = {"fields": fields}
        res = JiraService.update_issue(user, issue_id, data)
        return json.dumps(res)
    except Exception as e:
        return f"Error updating issue: {e}"


jira_update_issue_tool = AgentTool(params=JiraUpdateIssueParams, function=jira_update_issue_func, pass_context=True)


class JiraTransitionIssueParams(BaseModel):
    issue_id: str = Field(description="ID or key of the issue")
    transition_id: str = Field(description="ID of the transition to apply")


def jira_transition_issue_func(issue_id: str, transition_id: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.transition_issue(user, issue_id, transition_id)
        return json.dumps(res)
    except Exception as e:
        return f"Error transitioning issue: {e}"


jira_transition_issue_tool = AgentTool(params=JiraTransitionIssueParams, function=jira_transition_issue_func, pass_context=True)


class JiraAssignIssueParams(BaseModel):
    issue_id: str = Field(description="ID or key of the issue")
    account_id: str = Field(description="Account ID of the assignee")


def jira_assign_issue_func(issue_id: str, account_id: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.assign_issue(user, issue_id, account_id)
        return json.dumps(res)
    except Exception as e:
        return f"Error assigning issue: {e}"


jira_assign_issue_tool = AgentTool(params=JiraAssignIssueParams, function=jira_assign_issue_func, pass_context=True)


class JiraUnassignIssueParams(BaseModel):
    issue_id: str = Field(description="ID or key of the issue to unassign")


def jira_unassign_issue_func(issue_id: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.unassign_issue(user, issue_id)
        return json.dumps(res)
    except Exception as e:
        return f"Error unassigning issue: {e}"


jira_unassign_issue_tool = AgentTool(params=JiraUnassignIssueParams, function=jira_unassign_issue_func, pass_context=True)


class JiraGetSprintsParams(BaseModel):
    board_id: str = Field(description="ID of the board to list sprints from")


def jira_get_sprints_func(board_id: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.list_sprints(user, board_id)
        return json.dumps(res)
    except Exception as e:
        return f"Error getting sprints: {e}"


jira_get_sprints_tool = AgentTool(params=JiraGetSprintsParams, function=jira_get_sprints_func, pass_context=True)


class JiraGetSprintIssuesParams(BaseModel):
    sprint_id: str = Field(description="ID of the sprint to retrieve issues from")


def jira_get_sprint_issues_func(sprint_id: str, context: dict) -> str:
    try:
        user = User.get_user(context["user_id"])
        res = JiraService.get_sprint_issues(user, sprint_id)
        return json.dumps(res)
    except Exception as e:
        return f"Error getting sprint issues: {e}"


jira_get_sprint_issues_tool = AgentTool(params=JiraGetSprintIssuesParams, function=jira_get_sprint_issues_func, pass_context=True)
