import asyncio
import os
from dedalus_mcp import MCPServer, HttpMethod, HttpRequest, get_context
from dedalus_mcp.auth import Connection, SecretKeys


async def main():
    asana_conn = Connection(
        name="asana",
        secrets=SecretKeys(token="ASANA_ACCESS_TOKEN"),
        base_url="https://app.asana.com/api/1.0",
        auth_header_format="Bearer {api_key}",
    )

    server = MCPServer(
        name="asana-mcp",
        connections=[asana_conn],
    )

    async def test_dispatch(path: str) -> dict:
        ctx = get_context()
        resp = await ctx.dispatch(
            "asana",
            HttpRequest(method=HttpMethod.GET, path=path),
        )
        if resp.success:
            return {"status": "success", "data": resp.response.body}
        return {"status": "error", "error": resp.error.message if resp.error else "Unknown error"}

    access_token = os.getenv("ASANA_ACCESS_TOKEN")
    if not access_token:
        print("Error: ASANA_ACCESS_TOKEN environment variable not set")
        return

    print("Testing Asana MCP Server...")
    print()

    print("1. List workspaces:")
    result = await test_dispatch("/workspaces")
    print(result)
    print()

    if result.get("status") == "success":
        data = result.get("data", {})
        workspaces = data.get("data", [])
        if workspaces:
            workspace_gid = workspaces[0]["gid"]
            print(f"2. List projects in workspace {workspaces[0]['name']}:")
            result = await test_dispatch(f"/workspaces/{workspace_gid}/projects")
            print(result)
            print()

            if result.get("status") == "success":
                projects = result.get("data", {}).get("data", [])
                if projects:
                    project_gid = projects[0]["gid"]
                    print(f"3. List tasks in project '{projects[0]['name']}':")
                    result = await test_dispatch(f"/projects/{project_gid}/tasks")
                    print(result)
                    print()

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())