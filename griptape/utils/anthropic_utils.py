from __future__ import annotations

import re

# Claude model families, and the minimum ``(major, minor)`` version within each family, that no
# longer accept the ``temperature``, ``top_p``, and ``top_k`` sampling parameters. A model in one of
# these families at or above the listed version has those parameters deprecated and must not receive
# them. New families or version thresholds are picked up everywhere by editing this mapping.
SAMPLING_PARAMS_DEPRECATED_MIN_VERSIONS: dict[str, tuple[int, int]] = {
    "opus": (4, 7),
}

# Captures the family, ``major``, and optional ``minor`` version from a Claude model identifier,
# e.g. ``claude-opus-4-7`` within ``us.anthropic.claude-opus-4-7-20251101-v1:0``. Plain aliases,
# provider prefixes, geographic inference-profile IDs, ARNs, and dated variants all embed this
# substring, so it is matched anywhere in the identifier. The minor version is optional because
# major-only releases omit it (``claude-opus-5``) and pre-4.6 snapshots replace it with a date
# (``claude-opus-4-20250514``); restricting it to one or two digits that are not followed by another
# digit keeps an eight-digit date from being read as the minor.
_CLAUDE_VERSION_PATTERN = re.compile(r"claude-([a-z]+)-(\d+)(?:-(\d{1,2})(?!\d))?")


def supports_sampling_params(model: str) -> bool:
    """Whether a Claude model accepts the temperature, top_p, and top_k sampling parameters.

    Support is derived from the Claude model family and version embedded in ``model`` rather than a
    hardcoded model id, so every model in an affected family at or above the deprecating version
    (for example every Opus release from 4.7 onward, including major-only ids like ``claude-opus-5``)
    is covered without a per-model change. A model whose minor version is absent is treated as ``.0``.
    """
    match = _CLAUDE_VERSION_PATTERN.search(model)
    if match is None:
        return True

    family, major = match.group(1), int(match.group(2))
    minor = int(match.group(3)) if match.group(3) is not None else 0
    min_deprecated_version = SAMPLING_PARAMS_DEPRECATED_MIN_VERSIONS.get(family)

    return min_deprecated_version is None or (major, minor) < min_deprecated_version
