# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv

load_dotenv()
import os
from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings
from asana import asana, asana_tools


def _disable_auto_output_schemas(server: MCPServer) -> None:
    server.tools._build_output_schema = lambda _fn: None


def create_server() -> MCPServer:
    return MCPServer(
        name="asana-mcp",
        connections=[asana],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai"),
    )


async def main() -> None:
    server = create_server()
    _disable_auto_output_schemas(server)
    server.collect(*asana_tools)
    await server.serve(port=8080)