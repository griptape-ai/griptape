from __future__ import annotations

import json
from typing import TYPE_CHECKING, Union

from attrs import Factory, define, field

from griptape.rules import BaseRule
from griptape.utils import J2

if TYPE_CHECKING:
    from schema import Schema


@define()
class JsonSchemaRule(BaseRule):
    value: Union[dict, Schema] = field(metadata={"serializable": True})
    generate_template: J2 = field(default=Factory(lambda: J2("rules/json_schema.j2")))

    def to_text(self) -> str:
        value = self.value if isinstance(self.value, dict) else self.value.json_schema("Output Schema")
        return self.generate_template.render(json_schema=json.dumps(value))
