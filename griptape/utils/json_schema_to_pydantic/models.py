from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SchemaType:
    """Represents a JSON Schema type"""

    name: str
    format: Optional[str] = None


@dataclass
class FieldConstraints:
    """Represents JSON Schema field constraints"""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    exclusive_minimum: Optional[float] = None
    exclusive_maximum: Optional[float] = None
    multiple_of: Optional[float] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: bool = False


@dataclass
class CombinerSchema:
    """Represents a JSON Schema combiner"""

    type: str  # 'allOf', 'anyOf', 'oneOf'
    schemas: List[dict]
    root_schema: dict
