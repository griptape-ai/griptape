from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.common import Reference


def references_from_artifacts(artifacts: list[TextArtifact]) -> list[Reference]:
    references = []

    for a in artifacts:
        if a.reference is not None and a.reference not in references:
            references.append(a.reference)

    return references
