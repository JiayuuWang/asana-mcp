import os
from dedalus_mcp.auth import Connection, SecretKeys

_BASE_URL = "https://app.asana.com/api/1.0"

asana = Connection(
    name="asana",
    secrets=SecretKeys(token="ASANA_ACCESS_TOKEN"),
    base_url=_BASE_URL,
    auth_header_format="Bearer {api_key}",
)

__all__ = ["asana"]