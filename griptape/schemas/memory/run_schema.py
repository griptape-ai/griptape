from __future__ import annotations
from typing import TYPE_CHECKING
from marshmallow import fields, post_load
from griptape.schemas import BaseSchema
from .subtask_run_schema import SubtaskRunSchema


class RunSchema(BaseSchema):
    class Meta:
        ordered = True

    id = fields.Str()
    input = fields.Str()
    output = fields.Str()
    subtask_runs = fields.List(fields.Nested(SubtaskRunSchema))

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.structure import Run

        return Run(**data)
