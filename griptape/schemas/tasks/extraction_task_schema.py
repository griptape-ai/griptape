from marshmallow import fields, post_load

from griptape.schemas import BaseTextInputTaskSchema, PolymorphicSchema


class ExtractionTaskSchema(BaseTextInputTaskSchema):
    extraction_engine = fields.Nested(PolymorphicSchema(), only=("id"), dump_only=True)
    args = fields.Dict()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import ExtractionTask

        return ExtractionTask(**data)
