from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseRulesetDriver

if TYPE_CHECKING:
    from griptape.rules import BaseRule


@define(kw_only=True)
class LocalRulesetDriver(BaseRulesetDriver):
    persist_dir: Optional[str] = field(default=None, metadata={"serializable": True})

    def load(self, ruleset_name: str) -> tuple[list[BaseRule], dict[str, Any]]:
        if self.persist_dir is None:
            return [], {}

        file_name = os.path.join(self.persist_dir, ruleset_name)

        if (
            file_name is not None
            and os.path.exists(file_name)
            and (loaded_str := Path(file_name).read_text()) is not None
        ):
            try:
                return self._from_ruleset_dict(json.loads(loaded_str))
            except Exception as e:
                raise ValueError(f"Unable to load data from {file_name}") from e

        if self.raise_not_found:
            raise ValueError(f"Ruleset not found with name {file_name}")
        return [], {}
