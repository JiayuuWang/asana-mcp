# Asana MCP Server

A Type 4 OAuth MCP server for Asana API, enabling AI assistants to interact with Asana workspaces, projects, tasks, and users.

## Features

- **Workspaces & Projects**: List workspaces and projects
- **Tasks**: List, get, create, update, and search tasks
- **Comments**: Add comments to tasks
- **Users & Teams**: List users and teams

## Setup

### 1. Create an Asana OAuth App

1. Go to [developers.asana.com](https://developers.asana.com) and create an app
2. Set the redirect URL to your Dedalus deployment URL
3. Configure the following scopes:
   - `default`

### 2. Environment Variables

Configure these environment variables:

```bash
OAUTH_ENABLED=true
OAUTH_AUTHORIZE_URL=https://app.asana.com/-/oauth_authorize
OAUTH_TOKEN_URL=https://app.asana.com/-/oauth_token
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_SCOPES_AVAILABLE=default
OAUTH_BASE_URL=https://app.asana.com/api/1.0

DEDALUS_API_KEY=dsk-live-...
DEDALUS_AS_URL=https://as.dedaluslabs.ai
```

## Tools

### Workspaces & Projects

- **list_workspaces**: List all workspaces the user has access to
- **list_projects**: List projects in a workspace or team

### Tasks

- **list_tasks**: List tasks with optional filters (assignee, project, completed status)
- **get_task**: Get a specific task by ID
- **create_task**: Create a new task in a workspace or project
- **update_task**: Update an existing task

### Comments

- **add_task_comment**: Add a comment/story to a task

### Users & Teams

- **list_users**: List users in a workspace
- **list_teams**: List teams in a workspace

## Usage

```python
from dedalus_mcp import runner

result = await runner.run(
    input="Show me all tasks in the Design project",
    mcp_servers=["dedalus-labs/asana-mcp"],
)
```

## API Reference

This server uses the [Asana REST API v1.0](https://developers.asana.com/docs).

## License

MIT