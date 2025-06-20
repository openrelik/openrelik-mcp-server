# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://wwworkflowapi.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""MCP server for accessing files and directories in OpenRelik."""

import json
import os
import re
import sys
import time

from fastmcp import FastMCP
from openrelik_api_client.api_client import APIClient
import openrelik_api_client.folders as folderapi
import openrelik_api_client.workflows as workflowapi
import requests


# Workaround for https://github.com/google/adk-python/issues/743
# TODO: Remove this workaround when the issue is fixed and use env variables directly.
OPENRELIK_API_URL = sys.argv[1] if len(sys.argv) > 1 else os.getenv("OPENRELIK_API_URL")
OPENRELIK_API_KEY = sys.argv[2] if len(sys.argv) > 2 else os.getenv("OPENRELIK_API_KEY")

# Create the API client. It will handle token refreshes automatically.
api_client = APIClient(OPENRELIK_API_URL, OPENRELIK_API_KEY)

mcp = FastMCP(
    "OpenRelik MCP Server",
    # version="0.1.0",
    # description="MCP tools to access files and directories in OpenRelik",
)

ARTIFACT_URL = (
    "https://gist.githubusercontent.com/hacktobeer/174882f8d9cbbd2b0728ca90cad04cfa/raw"
)
ARTIFACTS_SUPPORTED = requests.get(ARTIFACT_URL).content


def remove_html_tags(text):
    """Remove html/pre tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def execute_workflow(root_folder, template_id, source_ids, template_data={}):
    # Create folder
    folder_id = folderapi.FoldersAPI(api_client).create_subfolder(
        root_folder, "extract_files"
    )
    print(f"Folder created {folder_id}")

    # Create workflow from TEMPLATE_ID
    workflow_id = workflowapi.WorkflowsAPI(api_client).create_workflow(
        folder_id, source_ids, template_id
    )
    print(f"Workflow ID: {workflow_id}")

    # Get workflow
    workflow = workflowapi.WorkflowsAPI(api_client).get_workflow(folder_id, workflow_id)

    # Update workflow to replace template markers to be replaced
    for key, value in template_data.items():
        workflow["spec_json"] = workflow["spec_json"].replace(key, value)
    workflowapi.WorkflowsAPI(api_client).update_workflow(
        folder_id, workflow_id, workflow
    )

    workflowapi.WorkflowsAPI(api_client).run_workflow(folder_id, workflow_id)

    # Poll workflow until finished
    while True:
        workflow = workflowapi.WorkflowsAPI(api_client).get_workflow(
            folder_id, workflow_id
        )
        # Check if all tasks are done in the workflow
        workflow_done = True
        for task in workflow["tasks"]:
            if task["status_short"] not in ["SUCCESS", "FAILURE"]:
                workflow_done = False

        if workflow_done:
            return json.dumps(workflow)
        time.sleep(1)


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
    # Bug, file content api return file with html tags aroung it...
    return remove_html_tags(str(response.content))


@mcp.tool(
    name="extract_file_from_disk_image",
    description="""
    Extracts a file from a disk image.
    NYou can give a file name (file_name) to be extracted from a disk image referenced
    with a file_id.
    NOTE: the filename should be a filename only, without the path component. For example, if you want
    to extract "/etc/ssh/sshd_config" you would give the file_name "sshd_config".
    On success returns a JSON string with the workflow results including output files (output_files)
    with their file id (id), folder location (folder_id) and display name (display_name).
    On failure returns a JSON string with the error (error_exception).
    """,
)
def extract_file_from_disk_image(file_name: str, file_id: int):
    ROOT_FOLDER = 305  # adk test folder
    TEMPLATE_ID = 2  # Extraction worker with <FILEPATH> marker

    template_data = {"<FILEPATH>": file_name}

    return execute_workflow(ROOT_FOLDER, TEMPLATE_ID, [file_id], template_data)


@mcp.tool(
    name="extract_artifact_from_disk_image",
    description="""
    Extracts an artifact from a disk image.
    The artifact_name should be a supported artifact as returned by tool `get_supported_extraction_artifacts`
    You can give a artifact name (artifact_name) to be extracted from a disk image referenced
    with a file_id.
    On success returns a JSON string with the workflow results including output files (output_files)
    with their file id (id), folder location (folder_id) and display name (display_name).
    On failure returns a JSON string with the error (error_exception).
    """,
)
def extract_artifact_from_disk_image(artifact_name: str, file_id: int):
    ROOT_FOLDER = 305  # adk test folder
    TEMPLATE_ID = 3  # Extraction worker with <FILEPATH> marker

    template_data = {"SshdConfigFile": artifact_name}

    return execute_workflow(ROOT_FOLDER, TEMPLATE_ID, [file_id], template_data)


@mcp.tool(
    name="get_supported_extraction_artifacts",
    description="""
    Gets the supported artifact (artifact_name) that can be used by the 
    `extract_artifact_from_disk_image` tool.
    Always returns a list of supported artifact names.
    """,
)
def get_supported_extraction_artifacts():
    return ARTIFACTS_SUPPORTED


@mcp.tool(
    name="create_forensic_timeline_from_disk_image",
    description="""
    Creates a forensic timeline from a disk image.
    The timeline output file will have the CSV format.
    On success returns a JSON string with the workflow results including output files (output_files)
    with their file id (id), folder location (folder_id) and display name (display_name).
    On failure returns a JSON string with the error (error_exception).
    """,
)
def create_forensic_timeline_from_disk_image(file_id: int):
    ROOT_FOLDER = 305  # adk test folder
    TEMPLATE_ID = 4  # Extraction worker with <FILEPATH> marker

    return execute_workflow(ROOT_FOLDER, TEMPLATE_ID, [file_id])


if __name__ == "__main__":
    mcp.run()
