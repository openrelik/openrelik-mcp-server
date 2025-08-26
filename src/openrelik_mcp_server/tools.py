import base64
from typing import Any

from .utils import get_openrelik_client

from fastmcp import FastMCP


mcp = FastMCP(
    "OpenRelik MCP Server",
)


def _read_file_metadata(file_id: int) -> dict[str, Any]:
    """Reads a file metadata from a file in OpenRelik. Always returns a JSON string with the file metadata.

    Args:
        file_id: The ID of the file to get the metadata from.

    Returns:
        A dictionary containing file metadata.
    """
    response = get_openrelik_client().get(f"/files/{file_id}")
    return response.json()


@mcp.tool()
def list_folder(folder_id: int) -> list[dict[str, Any]]:
    """Lists files in an OpenRelik folder. Always returns a JSON string with the list of files with
    their metadata.

    Args:
        folder_id: The ID of the folder to list the files from.

    Returns:
        A list of dictionaries containing file metadata, including:
        - display_name: The name of the file
        - filesize: The size of the file in bytes
        - magic_mime: The mime type of the file
    """
    response = get_openrelik_client().get(f"/folders/{folder_id}/files/")
    return response.json()


@mcp.tool()
def read_file_metadata(file_id: int) -> dict[str, Any]:
    """Reads a file metadata from a file in OpenRelik. Always returns a JSON string with the file metadata.

    Args:
        file_id: The ID of the file to get the metadata from.

    Returns:
        A dictionary containing file metadata, including:
        - display_name: The name of the file
        - filesize: The size of the file in bytes
        - extension: The extension of the file
        - original_path: The original path of the file where it was found on disk
        - magic_mime: The mime type of the file
        - hash_*: Several calculated unique forensic file hashes
    """
    response = _read_file_metadata(file_id)
    return response


@mcp.tool()
def read_file_content(file_id: int) -> bytes | str:
    """Reads the content of a file in OpenRelik. Returns the file content or
    an error if the filesize is too big (> 5MB)

    Args:
        file_id: The ID of the file to read the content from.

    Returns:
        The content of the file.
    """
    metadata = _read_file_metadata(file_id)
    if metadata.get("filesize") and metadata["filesize"] > 5_000_000:  # 10MB
        return f"Error read_file_content: Filesize too big (max 5MB) - {metadata['filesize']}"

    response = get_openrelik_client().get(f"/files/{file_id}/download")
    return base64.b64decode(response.content)
