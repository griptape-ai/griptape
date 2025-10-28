from typing import Annotated, Any, Callable, Dict, List, Literal, Type, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    RootModel,
    create_model,
)

from .exceptions import CombinerError
from .interfaces import (
    ICombinerHandler,
    IConstraintBuilder,
    IReferenceResolver,
    ITypeResolver,
)


class CombinerHandler(ICombinerHandler):
    """Handles JSON Schema combiners (allOf, anyOf, oneOf)"""

    def __init__(
        self,
        type_resolver: ITypeResolver,
        constraint_builder: IConstraintBuilder,
        reference_resolver: IReferenceResolver,
        recursive_field_builder: Callable,
        field_info_builder: Callable,
    ):
        # Store injected dependencies
        self.type_resolver = type_resolver
        self.constraint_builder = constraint_builder
        self.reference_resolver = reference_resolver
        # Store callbacks for recursive building
        self.recursive_field_builder = recursive_field_builder
        self.field_info_builder = field_info_builder

    def handle_all_of(
        self,
        schemas: List[Dict[str, Any]],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Type[BaseModel]:
        """Combines multiple schemas with AND logic."""
        if not schemas:
            raise CombinerError("allOf must contain at least one schema")

        merged_properties = {}
        required_fields = set()

        for schema in schemas:
            if not isinstance(schema, dict):
                raise CombinerError(f"Invalid schema in allOf: {schema}")

            # Resolve top-level $ref
            if "$ref" in schema:
                schema = self.reference_resolver.resolve_ref(
                    schema["$ref"], schema, root_schema
                )

            properties = schema.get("properties", {})
            required = schema.get("required", [])

            for prop_name, prop_schema in properties.items():
                if prop_name in merged_properties:
                    # Merge constraints for existing property using the injected constraint_builder
                    merged_properties[prop_name] = (
                        self.constraint_builder.merge_constraints(
                            merged_properties[prop_name], prop_schema
                        )
                    )
                else:
                    merged_properties[prop_name] = prop_schema

            required_fields.update(required)

        # Build field definitions using the callbacks
        field_definitions = {}
        for name, prop_schema in merged_properties.items():
            field_type = self.recursive_field_builder(
                prop_schema, root_schema, allow_undefined_array_items
            )
            field_info = self.field_info_builder(prop_schema, name in required_fields)
            field_definitions[name] = (field_type, field_info)

        return create_model(
            "AllOfModel",
            __config__=ConfigDict(extra="forbid"),
            **field_definitions,
        )

    def handle_any_of(
        self,
        schemas: List[Dict[str, Any]],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Allows validation against any of the given schemas."""
        if not schemas:
            raise CombinerError("anyOf must contain at least one schema")

        possible_types = []
        for schema in schemas:
            if not isinstance(schema, dict):
                raise CombinerError(f"Invalid schema in anyOf: {schema}")

            # Resolve $ref if present
            if "$ref" in schema:
                schema = self.reference_resolver.resolve_ref(
                    schema["$ref"], schema, root_schema
                )

            # Use the recursive_field_builder callback to resolve the type
            resolved_type = self.recursive_field_builder(
                schema, root_schema, allow_undefined_array_items
            )
            possible_types.append(resolved_type)

        return Union[tuple(possible_types)]

    def handle_one_of(
        self,
        schema: Dict[str, Any],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Type[BaseModel]:
        """Implements discriminated unions using a type field."""
        schemas = schema.get("oneOf", [])
        if not schemas:
            raise CombinerError("oneOf must contain at least one schema")

        # Create a model for each variant
        variant_models = {}

        for variant_schema in schemas:
            if not isinstance(variant_schema, dict):
                raise CombinerError(f"Invalid schema in oneOf: {variant_schema}")

            # Resolve $ref if present at the variant level
            ref_path = None  # Initialize ref_path
            if "$ref" in variant_schema:
                ref_path = variant_schema["$ref"]  # Store the ref path
                variant_schema = self.reference_resolver.resolve_ref(
                    ref_path, variant_schema, root_schema
                )

            properties = variant_schema.get("properties", {})
            type_const = properties.get("type", {}).get("const")
            if not type_const:
                raise CombinerError("Each oneOf variant must have a type const")

            # Create field definitions for this variant
            fields = {}
            required = variant_schema.get("required", [])

            for name, prop_schema in properties.items():
                if name == "type":
                    description = prop_schema.get("description")
                    fields[name] = (
                        Literal[type_const],
                        Field(default=type_const, description=description),
                    )
                elif "oneOf" in prop_schema:
                    # Handle nested oneOf using the callback
                    field_type = self.recursive_field_builder(
                        prop_schema, root_schema, allow_undefined_array_items
                    )
                    # Use field_info_builder for nested oneOf field info
                    field_info = self.field_info_builder(prop_schema, name in required)
                    fields[name] = (field_type, field_info)
                # Add other properties to the fields dictionary
                elif name != "type":  # Skip the type field as it's handled above
                    field_type = self.recursive_field_builder(
                        prop_schema, root_schema, allow_undefined_array_items
                    )
                    field_info = self.field_info_builder(prop_schema, name in required)
                    fields[name] = (field_type, field_info)

            # Create model for this variant
            # Use the name from the $ref if available, otherwise generate one
            if ref_path:
                model_name = ref_path.split("/")[-1]  # Extract name from ref
            else:
                model_name = f"Variant_{type_const}"

            variant_model = create_model(
                model_name, __config__=ConfigDict(extra="forbid"), **fields
            )
            variant_models[type_const] = variant_model

        # Always wrap in RootModel for consistent access pattern
        if len(variant_models) == 1:
            return RootModel[list(variant_models.values())[0]]
        else:
            union_type = Annotated[
                Union[tuple(variant_models.values())],
                Discriminator(discriminator="type"),
            ]
            return RootModel[union_type]
