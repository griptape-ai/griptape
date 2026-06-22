from __future__ import annotations

from griptape.exceptions.griptape_error import GriptapeError


class PromptDriverError(GriptapeError):
    """Raised when a Prompt Driver's underlying provider call fails.

    The original provider SDK exception is preserved as this error's ``__cause__``
    (drivers re-raise with ``raise ... from``), so callers can still inspect it.
    ``status_code`` is populated for HTTP-style failures (e.g. 401, 429) and is
    ``None`` for non-HTTP failures such as connection errors.
    """

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
