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
"""Utilities for OpenRelik MCP server."""

import os
from typing import Dict, Optional

from openrelik_api_client.api_client import APIClient


def get_openrelik_client() -> APIClient:
    """
    Gets an instance of the OpenRelik API client.

    Returns:
        APIClient: The API client instance.

    Raises:
        RuntimeError: If either OPENRELIK_API_URL or OPENRELIK_API_KEY is not set.
    """
    env_vars: Dict[str, Optional[str]] = {
        "OPENRELIK_API_URL": os.getenv("OPENRELIK_API_URL"),
        "OPENRELIK_API_KEY": os.getenv("OPENRELIK_API_KEY"),
    }
    missing_vars = [key for key, value in env_vars.items() if not value]

    if missing_vars:
        raise RuntimeError(
            f"The following environment variables are not set: {', '.join(missing_vars)}"
        )

    return APIClient(env_vars["OPENRELIK_API_URL"], env_vars["OPENRELIK_API_KEY"])
