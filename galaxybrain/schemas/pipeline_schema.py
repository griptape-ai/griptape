from marshmallow import post_load
from galaxybrain.schemas.structure_schema import StructureSchema


class PipelineSchema(StructureSchema):
    @post_load
    def make_structure(self, data, **kwargs):
        from galaxybrain.structures import Pipeline

        pipeline = Pipeline(**data)

        for step in pipeline.steps:
            step.structure = pipeline

        return pipeline
