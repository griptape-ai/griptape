from __future__ import annotations

import json

from attrs import define, field

from griptape.rules import BaseRule
from griptape.utils import J2


@define(frozen=True)
class JsonSchemaRule(BaseRule):
    value: dict = field()
    template_generator: J2 = field(default=J2("rules/json_schema.j2"))

    def to_text(self) -> str:
        return self.template_generator.render(json_schema=json.dumps(self.value))
