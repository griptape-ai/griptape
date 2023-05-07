import functools
import schema
from schema import Schema


def activity(config: dict):
    validated_config = __config_schema().validate(config)
    validated_config.update(
        {k: v for k, v in config.items() if k not in validated_config}
    )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        if not validated_config.get("schema"):
            validated_config["schema"] = None

        wrapper.config = validated_config
        wrapper.is_activity = True

        return wrapper
    return decorator


def __config_schema() -> Schema:
    return Schema({
        "name": str,
        "description": str,
        schema.Optional("schema"): Schema,
        schema.Optional("require_ramp", default=False): bool
    }, ignore_extra_keys=True)
