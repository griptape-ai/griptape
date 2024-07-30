from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from typing import Any, Literal, Union, _SpecialForm, get_args, get_origin

import attrs
from marshmallow import INCLUDE, Schema, fields

from griptape.schemas.bytes_field import Bytes


class BaseSchema(Schema):
    class Meta:
        unknown = INCLUDE

    DATACLASS_TYPE_MAPPING = {**Schema.TYPE_MAPPING, dict: fields.Dict, bytes: Bytes, Any: fields.Raw}

    @classmethod
    def from_attrs_cls(cls, attrs_cls: type) -> type:
        """Generate a Schema from an attrs class.

        Args:
            attrs_cls: An attrs class.
        """
        from marshmallow import post_load

        from griptape.mixins import SerializableMixin

        class SubSchema(cls):
            @post_load
            def make_obj(self, data: Any, **kwargs) -> Any:
                return attrs_cls(**data)

        if issubclass(attrs_cls, SerializableMixin):
            cls._resolve_types(attrs_cls)
            return SubSchema.from_dict(
                {
                    a.name: cls._get_field_for_type(a.type)
                    for a in attrs.fields(attrs_cls)
                    if a.metadata.get("serializable")
                },
                name=f"{attrs_cls.__name__}Schema",
            )
        else:
            raise ValueError(f"Class must implement SerializableMixin: {attrs_cls}")

    @classmethod
    def _get_field_for_type(cls, field_type: type) -> fields.Field | fields.Nested:
        """Generate a marshmallow Field instance from a Python type.

        Args:
            field_type: A field type.
        """
        from griptape.schemas.polymorphic_schema import PolymorphicSchema

        field_class, args, optional = cls._get_field_type_info(field_type)

        if attrs.has(field_class):
            if ABC in field_class.__bases__:
                return fields.Nested(PolymorphicSchema(inner_class=field_class), allow_none=optional)
            else:
                return fields.Nested(cls.from_attrs_cls(field_class), allow_none=optional)
        elif cls.is_list_sequence(field_class):
            if args:
                return fields.List(cls_or_instance=cls._get_field_for_type(args[0]), allow_none=optional)
            else:
                raise ValueError(f"Missing type for list field: {field_type}")
        else:
            field_class = cls.DATACLASS_TYPE_MAPPING[field_class]

            return field_class(allow_none=optional)

    @classmethod
    def _get_field_type_info(cls, field_type: type) -> tuple[type, tuple[type, ...], bool]:
        """Get information about a field type.

        Args:
            field_type: A field type.
        """
        origin = get_origin(field_type) or field_type
        args = get_args(field_type)
        optional = False

        if origin is Union:
            origin = args[0]
            if len(args) > 1 and args[1] is type(None):
                optional = True

            origin, args, _ = cls._get_field_type_info(origin)
        elif origin is Literal:
            origin = type(args[0])
            args = ()

        return origin, args, optional

    @classmethod
    def _resolve_types(cls, attrs_cls: type) -> None:
        """Resolve types in an attrs class.

        Args:
            attrs_cls: An attrs class.
        """
        from collections.abc import Sequence
        from typing import Any

        from griptape.artifacts import BaseArtifact
        from griptape.common import (
            BaseDeltaMessageContent,
            BaseMessageContent,
            Message,
            PromptStack,
            Reference,
            ToolAction,
        )
        from griptape.drivers import (
            BaseAudioTranscriptionDriver,
            BaseConversationMemoryDriver,
            BaseEmbeddingDriver,
            BaseImageGenerationDriver,
            BaseImageQueryDriver,
            BasePromptDriver,
            BaseTextToSpeechDriver,
            BaseVectorStoreDriver,
        )
        from griptape.events import EventListener
        from griptape.memory.structure import Run
        from griptape.structures import Structure
        from griptape.tokenizers import BaseTokenizer
        from griptape.tools import BaseTool
        from griptape.utils import import_optional_dependency, is_dependency_installed

        attrs.resolve_types(
            attrs_cls,
            localns={
                "Any": Any,
                "BasePromptDriver": BasePromptDriver,
                "BaseImageQueryDriver": BaseImageQueryDriver,
                "BaseEmbeddingDriver": BaseEmbeddingDriver,
                "BaseVectorStoreDriver": BaseVectorStoreDriver,
                "BaseTextToSpeechDriver": BaseTextToSpeechDriver,
                "BaseAudioTranscriptionDriver": BaseAudioTranscriptionDriver,
                "BaseConversationMemoryDriver": BaseConversationMemoryDriver,
                "BaseImageGenerationDriver": BaseImageGenerationDriver,
                "BaseArtifact": BaseArtifact,
                "PromptStack": PromptStack,
                "EventListener": EventListener,
                "BaseMessageContent": BaseMessageContent,
                "BaseDeltaMessageContent": BaseDeltaMessageContent,
                "BaseTool": BaseTool,
                "Usage": Message.Usage,
                "Structure": Structure,
                "BaseTokenizer": BaseTokenizer,
                "ToolAction": ToolAction,
                "Reference": Reference,
                "Run": Run,
                "Sequence": Sequence,
                # Third party modules
                "Client": import_optional_dependency("cohere").Client if is_dependency_installed("cohere") else Any,
                "GenerativeModel": import_optional_dependency("google.generativeai").GenerativeModel
                if is_dependency_installed("google.generativeai")
                else Any,
                "boto3": import_optional_dependency("boto3") if is_dependency_installed("boto3") else Any,
            },
        )

    @classmethod
    def is_list_sequence(cls, field_type: type | _SpecialForm) -> bool:
        if isinstance(field_type, type):
            if issubclass(field_type, str) or issubclass(field_type, bytes) or issubclass(field_type, tuple):
                return False
            else:
                return issubclass(field_type, Sequence)
        else:
            return False
