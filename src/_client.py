# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the Asana MCP server.

Runs against the deployed marketplace server via the Dedalus runner,
passing credentials through the DAuth SecretValues path (the same path a
real marketplace user hits). Every tool is exercised at least once and a
deterministic PASS/FAIL line is printed per tool.

Required environment variables:
    DEDALUS_API_KEY       Dedalus API key (dsk-live-...)
    ASANA_ACCESS_TOKEN    Asana personal access token / OAuth token

Optional:
    DEDALUS_API_URL   Override Dedalus API base (default https://api.dedaluslabs.ai)
    DEDALUS_AS_URL    Override Dedalus AS base  (default https://as.dedaluslabs.ai)
    MCP_SERVER_SLUG   Marketplace slug (default JiayuWang/asana-mcp)

Usage:
    PYTHONPATH=src python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from asana import asana  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang(王嘉宇)/asana-mcp")
MODEL = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

REQUIRED_TOOLS = [
    "list_workspaces",
    "list_projects",
    "list_tasks",
    "get_task",
    "list_users",
    "list_teams",
    "create_task",
    "update_task",
    "add_task_comment",
]


def _passed(tool_name: str, output: str) -> bool:
    if not output:
        return False
    lowered = output.lower()
    hard_failures = (
        "no tool",
        "tool not found",
        "unknown tool",
        "could not call",
        "no active context",
        "modulenotfounderror",
        "importerror",
        "currently unavailable",
        "mcp server",
    )
    return not any(marker in lowered for marker in hard_failures)


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=6,
            max_tokens=4096,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:600])
        ok = _passed(tool_name, output)
    except Exception as exc:  # noqa: BLE001
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set")
        return 1
    if not ASANA_ACCESS_TOKEN:
        print("Error: ASANA_ACCESS_TOKEN not set")
        return 1

    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    creds = [SecretValues(_rebind(asana, MCP_SERVER_SLUG), token=ASANA_ACCESS_TOKEN)]

    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,
    )
    runner = DedalusRunner(client)

    print(f"Testing Asana MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    # 1. Read-only discovery. list_workspaces yields the workspace gid that
    #    almost every other Asana tool requires.
    results["list_workspaces"] = await _run_tool(
        runner, creds, "list_workspaces",
        "Call the list_workspaces tool and show each workspace gid and name.",
    )
    results["list_projects"] = await _run_tool(
        runner, creds, "list_projects",
        "Call list_workspaces to get the first workspace gid, then call "
        "list_projects for that workspace and list each project gid and name.",
    )
    results["list_tasks"] = await _run_tool(
        runner, creds, "list_tasks",
        "Call list_workspaces to get the first workspace gid, then call "
        "list_tasks for that workspace with limit 5 and list each task gid.",
    )
    results["get_task"] = await _run_tool(
        runner, creds, "get_task",
        "Call list_workspaces, then list_tasks with limit 1 to get a task gid, "
        "then call get_task on that gid and show its name.",
    )
    results["list_users"] = await _run_tool(
        runner, creds, "list_users",
        "Call list_workspaces to get the first workspace gid, then call "
        "list_users for that workspace and list each user name.",
    )
    results["list_teams"] = await _run_tool(
        runner, creds, "list_teams",
        "Call list_workspaces to get the first workspace gid, then call "
        "list_teams for that workspace and list each team name.",
    )

    # 2. Write tools, run against an isolated smoke-test task. create_task ->
    #    update_task -> add_task_comment all operate on the task we create, so
    #    the fixture is self-contained.
    results["create_task"] = await _run_tool(
        runner, creds, "create_task",
        "Call list_workspaces to get the first workspace gid, then call "
        "create_task with name 'Dedalus Smoke Test Task' in that workspace. "
        "Report the new task gid.",
    )
    results["update_task"] = await _run_tool(
        runner, creds, "update_task",
        "Call list_workspaces, create_task with name 'Dedalus Update Test' to "
        "get a task gid, then call update_task on that gid setting notes to "
        "'updated by dedalus smoke test'.",
    )
    results["add_task_comment"] = await _run_tool(
        runner, creds, "add_task_comment",
        "Call list_workspaces, create_task with name 'Dedalus Comment Test' to "
        "get a task gid, then call add_task_comment on that gid with text "
        "'dedalus smoke test comment'.",
    )

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))