from marshmallow import post_load, fields
from griptape.schemas import StructureSchema


class PipelineSchema(StructureSchema):
    autoprune_memory = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.structures import Pipeline

        return Pipeline(**data)
