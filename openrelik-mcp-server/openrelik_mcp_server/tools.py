from .utils import get_openrelik_client

from fastmcp import FastMCP


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
    response = get_openrelik_client().get(f"/folders/{folder_id}/files/")
    return response.json()


@mcp.tool(
    name="read_file_metadata",
    description="""
    Reads a file metadata from a file in OpenRelik. Always returns a JSON string with the file metadata.
    """,
)
def read_file_metadata(file_id: int) -> str:
    """Reads a file metadata from a file in OpenRelik."""
    response = get_openrelik_client().get(f"/files/{file_id}")
    return response.json()


@mcp.tool(
    name="read_file_content",
    description="""
    Reads the content of a file in OpenRelik. Always returns a JSON string with the file content.
    """,
)
def read_file_content(file_id: int) -> str:
    """Reads a file content from a file in OpenRelik."""
    response = get_openrelik_client().get(f"/files/{file_id}/content/")
    return response.json()
