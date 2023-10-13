from __future__ import annotations
from marshmallow import post_load, fields
from griptape.schemas import PolymorphicSchema, BaseTextInputTaskSchema


class TextSummaryTaskSchema(BaseTextInputTaskSchema):
    summary_engine = fields.Nested(PolymorphicSchema(), only=("id"), dump_only=True)

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import TextSummaryTask

        return TextSummaryTask(**data)
