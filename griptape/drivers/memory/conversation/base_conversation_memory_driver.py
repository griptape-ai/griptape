from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.memory.structure import Run


class BaseConversationMemoryDriver(SerializableMixin, ABC):
    @abstractmethod
    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None: ...

    @abstractmethod
    def load(self) -> tuple[list[Run], dict[str, Any]]: ...

    def _to_params_dict(self, runs: list[Run], metadata: dict[str, Any]) -> dict:
        return {"runs": [run.to_dict() for run in runs], "metadata": metadata}

    def _from_params_dict(self, params_dict: dict[str, Any]) -> tuple[list[Run], dict[str, Any]]:
        from griptape.memory.structure import Run

        return [Run.from_dict(run) for run in params_dict.get("runs", [])], params_dict.get("metadata", {})
