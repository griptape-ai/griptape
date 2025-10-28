from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ITypeResolver(ABC):
    @abstractmethod
    def resolve_type(
        self,
        schema: Dict[str, Any],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Resolves JSON Schema types to Pydantic types"""
        pass


class IConstraintBuilder(ABC):
    @abstractmethod
    def build_constraints(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Builds Pydantic field constraints from JSON Schema"""
        pass


class ICombinerHandler(ABC):
    @abstractmethod
    def handle_all_of(
        self,
        schemas: List[Dict[str, Any]],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Handles allOf combiner"""
        pass

    @abstractmethod
    def handle_any_of(
        self,
        schemas: List[Dict[str, Any]],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Handles anyOf combiner"""
        pass

    @abstractmethod
    def handle_one_of(
        self,
        schema: Dict[str, Any],
        root_schema: Dict[str, Any],
        allow_undefined_array_items: bool = False,
    ) -> Any:
        """Handles oneOf combiner"""
        pass


class IReferenceResolver(ABC):
    @abstractmethod
    def resolve_ref(
        self, ref: str, schema: Dict[str, Any], root_schema: Dict[str, Any]
    ) -> Any:
        """Resolves JSON Schema references"""
        pass


class IModelBuilder(ABC, Generic[T]):
    @abstractmethod
    def create_pydantic_model(
        self,
        schema: Dict[str, Any],
        root_schema: Optional[Dict[str, Any]] = None,
        allow_undefined_array_items: bool = False,
    ) -> Type[T]:
        """Creates a Pydantic model from JSON Schema"""
        pass
