from __future__ import annotations

import os
from abc import ABC
from typing import Optional

from attrs import Factory, define, field

from griptape.tools import BaseTool


@define
class BaseGriptapeCloudTool(BaseTool, ABC):
    """Base class for Griptape Cloud clients.

    Attributes:
        base_url: Base URL for the Griptape Cloud Knowledge Base API.
        api_key: API key for Griptape Cloud.
        headers: Headers for the Griptape Cloud Knowledge Base API.
    """

    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
        kw_only=True,
    )
    api_key: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")), kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
