from __future__ import annotations


class GriptapeError(Exception):
    """Base class for Griptape's typed exceptions.

    New Griptape exception types should inherit from this so callers can catch them
    all with a single ``except GriptapeError``.
    """
