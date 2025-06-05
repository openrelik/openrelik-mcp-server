# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""MCP server for accessing files and directories in OpenRelik."""

import os
import sys

from fastmcp import FastMCP
from openrelik_api_client.api_client import APIClient

# Workaround for https://github.com/google/adk-python/issues/743
# TODO: Remove this workaround when the issue is fixed and use env variables directly.
OPENRELIK_API_URL = sys.argv[1] if len(sys.argv) > 1 else os.getenv("OPENRELIK_API_URL")
OPENRELIK_API_KEY = sys.argv[2] if len(sys.argv) > 2 else os.getenv("OPENRELIK_API_KEY")

# Create the API client. It will handle token refreshes automatically.
api_client = APIClient(OPENRELIK_API_URL, OPENRELIK_API_KEY)

mcp = FastMCP(
    "OpenRelik MCP Server",
    version="0.1.0",
    description="MCP tools to access files and directories in OpenRelik",
)


@mcp.tool(
    name="list_folder",
    description="""
    Lists files in an OpenRelik folder. Always returns a JSON string with the list of files with
    their metadata.
    """,
)
def list_folder(folder_id: int) -> str:
    """Lists files in an OpenRelik folder."""
    response = api_client.get(f"/folders/{folder_id}/files/")
    return response.text


@mcp.tool(
    name="read_file_metadata",
    description="""
    Reads a file metadata from a file in OpenRelik. Always returns a JSON string with the file metadata.
    """,
)
def read_file_metadata(file_id: int) -> str:
    """Reads a file metadata from a file in OpenRelik."""
    response = api_client.get(f"/files/{file_id}")
    return response.json()


@mcp.tool(
    name="read_file_content",
    description="""
    Reads the content of a file in OpenRelik. Always returns a JSON string with the file content.
    """,
)
def read_file_content(file_id: int) -> str:
    """Reads a file metadata from a file in OpenRelik."""
    response = api_client.get(f"/files/{file_id}/content/")
    return response.content


if __name__ == "__main__":
    mcp.run()
