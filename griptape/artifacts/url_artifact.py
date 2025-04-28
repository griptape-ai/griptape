from __future__ import annotations

import requests
from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class UrlArtifact(BaseArtifact):
    """Stores a url.

    Attributes:
        value: The url.
    """

    value: str = field(metadata={"serializable": True})

    def to_bytes(self, *, headers: dict | None = None, **kwargs: dict) -> bytes:
        """Fetches the content of the URL and returns it as bytes.

        Args:
            headers: Optional headers to include in the request.
            **kwargs: Additional keyword arguments, not used.

        Returns:
            bytes: The content of the URL as bytes.

        """
        response = requests.get(self.value, headers=headers)
        response.raise_for_status()

        return response.content

    def to_text(self) -> str:
        """Returns the URL as is."""
        return self.value
