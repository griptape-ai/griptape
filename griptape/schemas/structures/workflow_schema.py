from marshmallow import post_load
from griptape.schemas import StructureSchema


class WorkflowSchema(StructureSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.structures import Workflow

        return Workflow(**data)
