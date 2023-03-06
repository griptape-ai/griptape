from marshmallow import post_load
from warpspeed.schemas.structure_schema import StructureSchema


class PipelineSchema(StructureSchema):
    @post_load
    def make_structure(self, data, **kwargs):
        from warpspeed.structures import Pipeline

        pipeline = Pipeline(**data)

        for step in pipeline.steps:
            step.structure = pipeline

        return pipeline
