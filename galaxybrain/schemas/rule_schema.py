from marshmallow import Schema, fields, post_load


class RuleSchema(Schema):
    value = fields.Str()

    @post_load
    def make_rule(self, data, **kwargs):
        from galaxybrain.rules import Rule

        return Rule(**data)
