from datetime import date, datetime, time
from typing import Any, Dict, Literal
from uuid import UUID

from pydantic import AnyUrl

from .interfaces import IConstraintBuilder

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class ConstraintBuilder(IConstraintBuilder):
    """Builds Pydantic field constraints from JSON Schema"""

    def build_constraints(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract field constraints from schema."""
        constraints = {}

        # String constraints
        if "minLength" in schema:
            constraints["min_length"] = schema["minLength"]
        if "maxLength" in schema:
            constraints["max_length"] = schema["maxLength"]
        if "pattern" in schema:
            constraints["pattern"] = schema["pattern"]
        # Handle const values first
        if "const" in schema:
            return Literal[schema["const"]]

        if "format" in schema:
            format_type = schema["format"]
            if format_type == "email":
                constraints["pattern"] = EMAIL_PATTERN
                return constraints
            elif format_type == "date-time":
                return datetime
            elif format_type == "date":
                return date
            elif format_type == "time":
                return time
            elif format_type == "uri":
                return AnyUrl
            elif format_type == "uuid":
                return UUID

        # Number constraints
        if "minimum" in schema:
            constraints["ge"] = schema["minimum"]
        if "maximum" in schema:
            constraints["le"] = schema["maximum"]
        if "exclusiveMinimum" in schema:
            constraints["gt"] = schema["exclusiveMinimum"]
        if "exclusiveMaximum" in schema:
            constraints["lt"] = schema["exclusiveMaximum"]
        if "multipleOf" in schema:
            constraints["multiple_of"] = schema["multipleOf"]

        # Array constraints
        if "minItems" in schema:
            constraints["min_length"] = schema["minItems"]
        if "maxItems" in schema:
            constraints["max_length"] = schema["maxItems"]

        return constraints

    def merge_constraints(
        self, schema1: Dict[str, Any], schema2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merges constraints from two schemas for the same property."""
        merged = schema1.copy()

        # Handle numeric constraints
        for constraint in [
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "multipleOf",
        ]:
            if constraint in schema2:
                if constraint in merged:
                    if "minimum" in constraint or "exclusiveMinimum" in constraint:
                        merged[constraint] = max(
                            merged[constraint], schema2[constraint]
                        )
                    else:
                        merged[constraint] = min(
                            merged[constraint], schema2[constraint]
                        )
                else:
                    merged[constraint] = schema2[constraint]

        # Handle string constraints
        for constraint in ["minLength", "maxLength", "pattern"]:
            if constraint in schema2:
                if constraint in merged:
                    if "min" in constraint.lower():
                        merged[constraint] = max(
                            merged[constraint], schema2[constraint]
                        )
                    elif "max" in constraint.lower():
                        merged[constraint] = min(
                            merged[constraint], schema2[constraint]
                        )
                    else:
                        # For pattern, combine with AND logic
                        merged[constraint] = (
                            f"(?={merged[constraint]})(?={schema2[constraint]})"
                        )
                else:
                    merged[constraint] = schema2[constraint]

        return merged
