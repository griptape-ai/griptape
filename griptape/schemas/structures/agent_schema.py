from marshmallow import post_load, fields
from griptape.schemas import StructureSchema, PolymorphicSchema


class AgentSchema(StructureSchema):
    task = fields.Nested(PolymorphicSchema())
    autoprune_memory = fields.Bool()

    @post_load
    def make_obj(self, data, **kwargs):
        from griptape.structures import Agent

        return Agent(**data)
