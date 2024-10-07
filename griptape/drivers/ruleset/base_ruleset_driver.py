from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.rules import BaseRule


@define
class BaseRulesetDriver(SerializableMixin, ABC):
    """Base class for ruleset drivers.

    Attributes:
        raise_not_found: Whether to raise an error if the ruleset is not found. Defaults to True.
    """

    raise_not_found: bool = field(default=True, kw_only=True, metadata={"serializable": True})

    @abstractmethod
    def load(self, ruleset_name: str) -> tuple[list[BaseRule], dict[str, Any]]: ...

    def _from_ruleset_dict(self, params_dict: dict[str, Any]) -> tuple[list[BaseRule], dict[str, Any]]:
        return [
            self._get_rule(rule["value"], rule.get("meta", {})) for rule in params_dict.get("rules", [])
        ], params_dict.get("meta", {})

    def _get_rule(self, value: Any, meta: dict[str, Any]) -> BaseRule:
        from griptape.rules import JsonSchemaRule, Rule

        return JsonSchemaRule(value=value, meta=meta) if isinstance(value, dict) else Rule(value=str(value), meta=meta)
