import json
from typing import Any

from mcp.types import TextContent
from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.types import ToolAnnotations

from asana.config import asana

Result = list[TextContent]


async def _req(
    method: HttpMethod,
    path: str,
    body: dict | None = None,
    params: dict | None = None,
) -> Result:
    ctx = get_context()
    resp = await ctx.dispatch(
        "JiayuWang(王嘉宇)-asana-mcp",
        HttpRequest(method=method, path=path, body=body, params=params),
    )
    if resp.success:
        data = resp.response.body or {}
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    error = resp.error.message if resp.error else "Request failed"
    return [TextContent(type="text", text=json.dumps({"error": error}, indent=2))]


@tool(
    description="List all workspaces the user has access to",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_workspaces() -> Result:
    return await _req(HttpMethod.GET, "/workspaces")


@tool(
    description="List projects in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_projects(
    workspace: str,
    team: str | None = None,
    limit: int = 100,
) -> Result:
    params: dict[str, Any] = {"limit": limit}
    if team:
        params["team"] = team
        return await _req(HttpMethod.GET, f"/teams/{team}/projects", params=params)
    return await _req(HttpMethod.GET, f"/workspaces/{workspace}/projects", params=params)


@tool(
    description="List tasks with optional filters",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_tasks(
    workspace: str,
    project: str | None = None,
    assignee: str | None = None,
    completed: bool | None = None,
    limit: int = 100,
) -> Result:
    params: dict[str, Any] = {"limit": limit}
    if assignee:
        params["assignee"] = assignee
    if completed is not None:
        params["completed"] = completed
    if project:
        return await _req(HttpMethod.GET, f"/projects/{project}/tasks", params=params)
    return await _req(HttpMethod.GET, f"/workspaces/{workspace}/tasks/search", params=params)


@tool(
    description="Get a specific task by ID",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_task(task_gid: str) -> Result:
    return await _req(HttpMethod.GET, f"/tasks/{task_gid}")


@tool(
    description="Create a new task",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_task(
    name: str,
    workspace: str,
    project: str | None = None,
    notes: str | None = None,
    assignee: str | None = None,
    completed: bool = False,
) -> Result:
    body: dict[str, Any] = {
        "data": {
            "name": name,
            "workspace": workspace,
            "completed": completed,
        }
    }
    if project:
        body["data"]["projects"] = [project]
    if notes:
        body["data"]["notes"] = notes
    if assignee:
        body["data"]["assignee"] = assignee
    return await _req(HttpMethod.POST, "/tasks", body=body)


@tool(
    description="Update an existing task",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def update_task(
    task_gid: str,
    name: str | None = None,
    notes: str | None = None,
    completed: bool | None = None,
    assignee: str | None = None,
) -> Result:
    body: dict[str, Any] = {"data": {}}
    if name is not None:
        body["data"]["name"] = name
    if notes is not None:
        body["data"]["notes"] = notes
    if completed is not None:
        body["data"]["completed"] = completed
    if assignee is not None:
        body["data"]["assignee"] = assignee
    return await _req(HttpMethod.PUT, f"/tasks/{task_gid}", body=body)


@tool(
    description="Add a comment/story to a task",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def add_task_comment(task_gid: str, text: str) -> Result:
    body = {
        "data": {
            "text": text,
        }
    }
    return await _req(HttpMethod.POST, f"/tasks/{task_gid}/stories", body=body)


@tool(
    description="List users in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_users(
    workspace: str,
    limit: int = 100,
) -> Result:
    params = {"limit": limit}
    return await _req(HttpMethod.GET, f"/workspaces/{workspace}/users", params=params)


@tool(
    description="List teams in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_teams(
    workspace: str,
    limit: int = 100,
) -> Result:
    params = {"limit": limit}
    return await _req(HttpMethod.GET, f"/workspaces/{workspace}/teams", params=params)


asana_tools = [
    list_workspaces,
    list_projects,
    list_tasks,
    get_task,
    create_task,
    update_task,
    add_task_comment,
    list_users,
    list_teams,
]