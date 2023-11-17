from marshmallow import fields, post_load
from griptape.schemas import BaseSchema


class TaskMemoryMetaEntrySchema(BaseSchema):
    output = fields.Str()
    task_memory_name = fields.Str()
    task_output_name = fields.Str()
    output_artifact_namespace = fields.Str()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.memory.meta import TaskMemoryMetaEntry

        return TaskMemoryMetaEntry(**data)
