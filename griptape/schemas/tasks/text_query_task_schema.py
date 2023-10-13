from __future__ import annotations
from marshmallow import post_load
from .base_text_input_task_schema import BaseTextInputTaskSchema


class TextQueryTaskSchema(BaseTextInputTaskSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.tasks import TextQueryTask

        return TextQueryTask(**data)
