from marshmallow import post_load, fields
from skatepark.schemas import StructureSchema


class PipelineSchema(StructureSchema):
    autoprune_memory = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.structures import Pipeline

        return Pipeline(**data)
