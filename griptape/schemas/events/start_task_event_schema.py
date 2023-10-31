from marshmallow import post_load
from .base_task_event_schema import BaseTaskEventSchema


class StartTaskEventSchema(BaseTaskEventSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.events import StartTaskEvent

        return StartTaskEvent(**data)
