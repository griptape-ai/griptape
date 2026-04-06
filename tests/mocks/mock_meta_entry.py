from __future__ import annotations

import json

from griptape.memory.meta import BaseMetaEntry


class MockMetaEntry(BaseMetaEntry):
    def to_json(self, *, serializable_overrides: dict[str, bool] | None = None) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self, *, serializable_overrides: dict[str, bool] | None = None) -> dict:
        return {"foo": "bar"}
