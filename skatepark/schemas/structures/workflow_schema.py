from marshmallow import post_load
from skatepark.schemas import StructureSchema


class WorkflowSchema(StructureSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from skatepark.structures import Workflow

        return Workflow(**data)
