from typing import Any, Dict, List, Optional, Set, Type, TypeVar

from pydantic import BaseModel, Field, create_model, ConfigDict

from .builders import ConstraintBuilder
from .handlers import CombinerHandler
from .interfaces import IModelBuilder
from .resolvers import ReferenceResolver, TypeResolver

T = TypeVar("T", bound=BaseModel)


class PydanticModelBuilder(IModelBuilder[T]):
    """Creates Pydantic models from JSON Schema definitions"""

    # Standard JSON Schema properties for fields
    STANDARD_FIELD_PROPERTIES = {
        "type", "format", "description", "default", "title", "examples",
        "const", "enum", "multipleOf", "maximum", "exclusiveMaximum", 
        "minimum", "exclusiveMinimum", "maxLength", "minLength", "pattern",
        "items", "additionalItems", "maxItems", "minItems", "uniqueItems",
        "properties", "additionalProperties", "required", "patternProperties",
        "dependencies", "propertyNames", "if", "then", "else", "allOf", 
        "anyOf", "oneOf", "not", "$ref", "$defs", "definitions"
    }
    
    # Standard JSON Schema properties for models  
    STANDARD_MODEL_PROPERTIES = {
        "type", "title", "description", "properties", "required", "additionalProperties",
        "patternProperties", "dependencies", "propertyNames", "if", "then", "else",
        "allOf", "anyOf", "oneOf", "not", "$ref", "$defs", "definitions", "$schema", 
        "$id", "$comment"
    }

    def __init__(self, base_model_type: Type[T] = BaseModel):
        # Instantiate resolvers and builders directly
        self.type_resolver = TypeResolver()
        self.constraint_builder = ConstraintBuilder()
        self.reference_resolver = ReferenceResolver()
        # Pass resolvers and method references as callbacks to CombinerHandler
        self.combiner_handler = CombinerHandler(
            type_resolver=self.type_resolver,
            constraint_builder=self.constraint_builder,
            reference_resolver=self.reference_resolver,
            recursive_field_builder=self._get_field_type,
            field_info_builder=self._build_field_info,
        )
        self.base_model_type = base_model_type
        # Track models being built to handle recursive references
        self._model_cache: Dict[str, Type[BaseModel]] = {}
        self._building_models: Set[str] = set()
        self._models_to_rebuild: Set[Type[BaseModel]] = set()

    def create_pydantic_model(
        self,
        schema: Dict[str, Any],
        root_schema: Optional[Dict[str, Any]] = None,
        allow_undefined_array_items: bool = False,
        _schema_ref: Optional[str] = None,
    ) -> Type[T]:
        """
        Creates a Pydantic model from a JSON Schema definition.

        Args:
            schema: The JSON Schema to convert
            root_schema: The root schema containing definitions

        Returns:
            A Pydantic model class
        """
        if root_schema is None:
            root_schema = schema

        # Store the original ref if present for tracking
        # Use the passed ref or extract from schema
        original_ref = _schema_ref or schema.get("$ref")
        
        # Handle references
        if "$ref" in schema:
            # Check if we've already built this model
            if original_ref in self._model_cache:
                return self._model_cache[original_ref]
            
            # Mark this ref as being built
            if original_ref:
                self._building_models.add(original_ref)
            
            schema = self.reference_resolver.resolve_ref(
                schema["$ref"],
                schema,
                root_schema,
            )

        # Handle combiners
        if "allOf" in schema:
            return self.combiner_handler.handle_all_of(
                schema["allOf"], root_schema, allow_undefined_array_items
            )
        if "anyOf" in schema:
            return self.combiner_handler.handle_any_of(
                schema["anyOf"], root_schema, allow_undefined_array_items
            )
        if "oneOf" in schema:
            return self.combiner_handler.handle_one_of(
                schema["oneOf"], root_schema, allow_undefined_array_items
            )

        # Get model properties
        # If this schema is referenced, use the ref name as the title if no title is provided
        if original_ref and "title" not in schema:
            ref_parts = original_ref.split("/")
            title = ref_parts[-1] if ref_parts else "DynamicModel"
        else:
            title = schema.get("title", "DynamicModel")
        description = schema.get("description")
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        # Extract model-level json_schema_extra
        model_extra = {
            key: value for key, value in schema.items()
            if key not in self.STANDARD_MODEL_PROPERTIES
        }

        # Build field definitions
        fields = {}
        for field_name, field_schema in properties.items():
            field_type = self._get_field_type(
                field_schema, root_schema, allow_undefined_array_items
            )
            field_info = self._build_field_info(field_schema, field_name in required)
            fields[field_name] = (field_type, field_info)

        # Create the model with or without json_schema_extra
        if model_extra:
            # Create a dynamic base class with the config
            class DynamicBase(self.base_model_type):
                model_config = ConfigDict(json_schema_extra=model_extra)
            
            model = create_model(title, __base__=DynamicBase, **fields)
        else:
            model = create_model(title, __base__=self.base_model_type, **fields)
            
        if description:
            model.__doc__ = description

        # Cache the model if it was referenced
        if original_ref:
            self._model_cache[original_ref] = model
            # Remove from building set
            self._building_models.discard(original_ref)
            # Mark model for rebuild after all models are created
            self._models_to_rebuild.add(model)

        # If this is the top-level call (no models being built), rebuild all models
        if not self._building_models and self._models_to_rebuild:
            # Build namespace with all models
            namespace = {m.__name__: m for m in self._models_to_rebuild}
            # Rebuild all models to resolve forward references
            for m in self._models_to_rebuild:
                m.model_rebuild(_types_namespace=namespace)
            # Clear the rebuild set
            self._models_to_rebuild.clear()

        return model

    def _get_field_type(
        self,
        field_schema: Dict[str, Any],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Resolves the Python type for a field schema."""
        # Store the original ref if present
        original_ref = field_schema.get("$ref")
        
        if "$ref" in field_schema:
            # Check if this reference is already being built (recursive reference)
            if original_ref in self._building_models:
                # Return cached model if available
                if original_ref in self._model_cache:
                    return self._model_cache[original_ref]
                # Otherwise, return a forward reference (string)
                # Extract model name from ref
                ref_parts = original_ref.split("/")
                model_name = ref_parts[-1] if ref_parts else "DynamicModel"
                return model_name
            
            # Check if we've already built this model
            if original_ref in self._model_cache:
                return self._model_cache[original_ref]
            
            # Mark this ref as being built before resolving
            self._building_models.add(original_ref)
            
            field_schema = self.reference_resolver.resolve_ref(
                field_schema["$ref"], field_schema, root_schema
            )

        # Handle combiners
        if "allOf" in field_schema:
            return self.combiner_handler.handle_all_of(
                field_schema["allOf"], root_schema, allow_undefined_array_items
            )
        if "anyOf" in field_schema:
            return self.combiner_handler.handle_any_of(
                field_schema["anyOf"], root_schema, allow_undefined_array_items
            )
        if "oneOf" in field_schema:
            return self.combiner_handler.handle_one_of(
                field_schema, root_schema, allow_undefined_array_items
            )

        # Handle arrays by recursively processing items
        if field_schema.get("type") == "array":
            items_schema = field_schema.get("items")
            if not items_schema:
                if allow_undefined_array_items:
                    return List[Any]
                else:
                    from .exceptions import TypeError
                    raise TypeError("Array type must specify 'items' schema")

            # Recursively process the items schema through the model builder
            # This ensures that object types get proper models created
            item_type = self._get_field_type(
                items_schema, root_schema, allow_undefined_array_items
            )
            
            if field_schema.get("uniqueItems", False):
                return Set[item_type]
            return List[item_type]

        # Handle nested objects by recursively creating models
        if field_schema.get("type") == "object" and "properties" in field_schema:
            # Build the model and cache/cleanup if we tracked this ref
            # Pass the original ref so the model can be named correctly
            model = self.create_pydantic_model(
                field_schema, root_schema, allow_undefined_array_items, _schema_ref=original_ref
            )
            
            # If we were tracking a ref for this field, cache and cleanup
            if original_ref and original_ref in self._building_models:
                self._model_cache[original_ref] = model
                self._building_models.discard(original_ref)
                # Mark model for rebuild after all models are created
                self._models_to_rebuild.add(model)
            
            return model

        return self.type_resolver.resolve_type(
            schema=field_schema,
            root_schema=root_schema,
            allow_undefined_array_items=allow_undefined_array_items,
        )

    def _build_field_info(self, field_schema: Dict[str, Any], required: bool) -> Field:
        """Creates a Pydantic Field with constraints from schema."""
        field_kwargs = {}

        # Add constraints
        constraints = self.constraint_builder.build_constraints(field_schema)
        if isinstance(constraints, type):
            pass  # Type will be handled by type_resolver
        elif isinstance(constraints, dict):
            field_kwargs.update(constraints)

        # Handle description
        if "description" in field_schema:
            field_kwargs["description"] = field_schema["description"]

        # Handle default value
        if "default" in field_schema:
            field_kwargs["default"] = field_schema["default"]
        elif not required:
            field_kwargs["default"] = None

        # Extract field-level json_schema_extra
        field_extra = {
            key: value for key, value in field_schema.items()
            if key not in self.STANDARD_FIELD_PROPERTIES
        }
        
        if field_extra:
            field_kwargs["json_schema_extra"] = field_extra

        return Field(**field_kwargs)
