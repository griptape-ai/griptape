from __future__ import annotations

import json

from attrs import Factory, define, field

from griptape.rules import BaseRule
from griptape.utils import J2


@define()
class JsonSchemaRule(BaseRule):
    value: dict = field(metadata={"serializable": True})
    generate_template: J2 = field(default=Factory(lambda: J2("rules/json_schema.j2")))

    def to_text(self) -> str:
        return self.generate_template.render(json_schema=json.dumps(self.value))
