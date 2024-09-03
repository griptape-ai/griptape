from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseConversationMemoryDriver

if TYPE_CHECKING:
    from griptape.memory.structure import Run


@define(kw_only=True)
class LocalConversationMemoryDriver(BaseConversationMemoryDriver):
    persist_file: Optional[str] = field(default=None, metadata={"serializable": True})

    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None:
        if self.persist_file is not None:
            Path(self.persist_file).write_text(json.dumps(self._to_params_dict(runs, metadata)))

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        if (
            self.persist_file is not None
            and os.path.exists(self.persist_file)
            and (loaded_str := Path(self.persist_file).read_text()) is not None
        ):
            try:
                return self._from_params_dict(json.loads(loaded_str))
            except Exception as e:
                raise ValueError(f"Unable to load data from {self.persist_file}") from e

        return [], {}
