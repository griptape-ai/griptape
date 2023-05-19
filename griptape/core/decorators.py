import functools
import schema
from schema import Schema
from griptape.artifacts import BaseArtifact

CONFIG_SCHEMA = Schema({
    "description": str,
    schema.Optional("schema"): Schema,
    schema.Optional("pass_artifacts"): bool
}, ignore_extra_keys=True)


def activity(config: dict):
    validated_config = CONFIG_SCHEMA.validate(config)

    validated_config.update(
        {k: v for k, v in config.items() if k not in validated_config}
    )

    if not validated_config.get("schema"):
        validated_config["schema"] = None

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, "artifacts"):
                artifacts = args[0].get("artifacts", {}).get("values", []) if len(args) > 0 else []

                self.artifacts = self.artifacts + [BaseArtifact.from_dict(artifact) for artifact in artifacts]

            return func(self, *args, **kwargs)

        wrapper.name = func.__name__
        wrapper.config = validated_config
        wrapper.is_activity = True

        return wrapper
    return decorator
