from datetime import date, datetime, time
from typing import Any, List, Literal, Optional, Set, Union
from uuid import UUID

from pydantic import AnyUrl

from .exceptions import ReferenceError, TypeError
from .interfaces import IReferenceResolver, ITypeResolver


class TypeResolver(ITypeResolver):
    """Resolves JSON Schema types to Pydantic types"""

    def resolve_type(
        self, schema: dict, root_schema: dict, allow_undefined_array_items: bool = False
    ) -> Any:
        """Get the Pydantic field type for a JSON schema field."""
        if not isinstance(schema, dict):
            raise TypeError(f"Invalid schema: expected dict, got {type(schema)}")

        # Handle references first
        if "$ref" in schema:
            reference_resolver = ReferenceResolver()
            schema = reference_resolver.resolve_ref(schema["$ref"], schema, root_schema)

        if "const" in schema:
            if schema["const"] is None:
                return type(None)
            return Literal[schema["const"]]

        if schema.get("type") == "null":
            return type(None)

        # Handle array of types (e.g. ["string", "null"])
        if isinstance(schema.get("type"), list):
            types = schema["type"]
            if "null" in types:
                other_types = [t for t in types if t != "null"]
                if len(other_types) == 0:
                    # Only null: {"type": ["null"]}
                    return type(None)
                elif len(other_types) == 1:
                    return Optional[
                        self.resolve_type(
                            schema={**schema, **{"type": other_types[0]}},
                            root_schema=root_schema,
                            allow_undefined_array_items=allow_undefined_array_items,
                        )
                    ]
                else:
                    # Multiple types with null: Union[type1, type2, ...] | None
                    resolved_types = [
                        self.resolve_type(
                            schema={**schema, **{"type": t}},
                            root_schema=root_schema,
                            allow_undefined_array_items=allow_undefined_array_items,
                        )
                        for t in other_types
                    ]
                    return Optional[Union[tuple(resolved_types)]]
            else:
                # No null in types
                if len(types) == 1:
                    # Single type in array: {"type": ["string"]}
                    return self.resolve_type(
                        schema={**schema, **{"type": types[0]}},
                        root_schema=root_schema,
                        allow_undefined_array_items=allow_undefined_array_items,
                    )
                else:
                    # Multiple types without null: Union[type1, type2, ...]
                    resolved_types = [
                        self.resolve_type(
                            schema={**schema, **{"type": t}},
                            root_schema=root_schema,
                            allow_undefined_array_items=allow_undefined_array_items,
                        )
                        for t in types
                    ]
                    return Union[tuple(resolved_types)]

        if "enum" in schema:
            if not schema["enum"]:
                raise TypeError("Enum must have at least one value")
            return Literal[tuple(schema["enum"])]

        # Infer type if not explicitly specified
        schema_type = schema.get("type")
        if not schema_type:
            # Infer type based on schema structure
            if "properties" in schema:
                schema_type = "object"
            elif "items" in schema:
                schema_type = "array"
            else:
                raise TypeError("Schema must specify a type")

        if schema_type == "array":
            items_schema = schema.get("items")
            if not items_schema:
                if allow_undefined_array_items:
                    return List[Any]  # Allow any type if items are not defined
                else:
                    raise TypeError("Array type must specify 'items' schema")

            # Handle references in array items
            if isinstance(items_schema, dict) and "$ref" in items_schema:
                # We need to resolve the reference before proceeding
                reference_resolver = ReferenceResolver()
                items_schema = reference_resolver.resolve_ref(
                    items_schema["$ref"], items_schema, root_schema
                )

            item_type = self.resolve_type(
                schema=items_schema,
                root_schema=root_schema,
                allow_undefined_array_items=allow_undefined_array_items,
            )
            if schema.get("uniqueItems", False):
                return Set[item_type]
            return List[item_type]

        # Handle format for string types
        if schema_type == "string" and "format" in schema:
            format_type = schema["format"]
            format_map = {
                "date-time": datetime,
                "date": date,
                "time": time,
                "email": str,
                "uri": AnyUrl,
                "uuid": UUID,
            }
            return format_map.get(format_type, str)

        if schema_type == "anyType":
            return Any

        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "object": dict,  # Will be replaced with actual model in builder
        }

        return type_map.get(schema_type, str)


class ReferenceResolver(IReferenceResolver):
    """Resolves JSON Schema references"""

    def __init__(self):
        self._processing_refs: Set[str] = set()

    def resolve_ref(self, ref: str, schema: dict, root_schema: dict) -> Any:
        """Resolve a JSON Schema $ref."""
        if not ref.startswith("#"):
            raise ReferenceError("Only local references (#/...) are supported")

        if ref in self._processing_refs:
            raise ReferenceError(f"Circular reference detected: {ref}")

        self._processing_refs.add(ref)
        try:
            # Split the reference path and navigate through the schema
            path = ref.split("/")[1:]  # Remove the '#' and split
            current = root_schema

            # Navigate through the schema
            for part in path:
                # Handle JSON Pointer escaping
                part = part.replace("~1", "/").replace("~0", "~")
                try:
                    current = current[part]
                except KeyError:
                    raise ReferenceError(f"Invalid reference path: {ref}")

            # If we find another reference, resolve it
            if isinstance(current, dict) and "$ref" in current:
                current = self.resolve_ref(current["$ref"], current, root_schema)

            return current
        finally:
            self._processing_refs.remove(ref)
