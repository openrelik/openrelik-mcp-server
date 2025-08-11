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

import json


import logging
import os
import sys
import time

from fastmcp import FastMCP
from openrelik_api_client.api_client import APIClient
import openrelik_api_client.workflows as workflowapi

import requests

logger = logging.getLogger(__name__)

OPENRELIK_API_URL = os.getenv("OPENRELIK_API_URL") or sys.argv[1]
OPENRELIK_API_KEY = os.getenv("OPENRELIK_API_KEY") or sys.argv[2]

# Create the API client. It will handle token refreshes automatically.
api_client = APIClient(OPENRELIK_API_URL, OPENRELIK_API_KEY)

mcp = FastMCP(
    "OpenRelik MCP Server",
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
    """Reads a file content from a file in OpenRelik."""
    response = api_client.get(f"/files/{file_id}/content/")
    # Bug workaround: file content api returns content with html tags around it for several mime types ...
    # This would not work if a file is indeed a HTML file...lol
    return response.text


if __name__ == "__main__":
    mcp.run()
