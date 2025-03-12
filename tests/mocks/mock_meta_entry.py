from __future__ import annotations

import json
from typing import Optional

from griptape.memory.meta import BaseMetaEntry


class MockMetaEntry(BaseMetaEntry):
    def to_json(self, *, serializable_overrides: Optional[dict[str, bool]] = None) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self, *, serializable_overrides: Optional[dict[str, bool]] = None) -> dict:
        return {"foo": "bar"}
