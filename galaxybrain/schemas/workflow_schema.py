from marshmallow import Schema, fields, post_load
from galaxybrain.schemas import PolymorphicSchema


class WorkflowSchema(Schema):
    prompt_driver = fields.Nested(PolymorphicSchema())
    steps = fields.List(fields.Nested(PolymorphicSchema()))

    @post_load
    def make_workflow(self, data, **kwargs):
        from galaxybrain.workflows import Workflow

        workflow = Workflow(**data)

        for step in workflow.steps:
            step.workflow = workflow

        return workflow
