import inspect
from typing import Optional, Callable
from attr import define, field
from jinja2 import Template
from schema import Schema


@define(slots=False)
class ActivityMixin:
    allowlist: Optional[list[str]] = field(default=None, kw_only=True)
    denylist: Optional[list[str]] = field(default=None, kw_only=True)

    @allowlist.validator
    def validate_allowlist(self, _, allowlist: Optional[list[str]]) -> None:
        if allowlist is None:
            return

        if self.denylist is not None:
            raise ValueError("can't have both allowlist and denylist specified")

        for activity_name in allowlist:
            self._validate_tool_activity(activity_name)

    @denylist.validator
    def validate_denylist(self, _, denylist: Optional[list[str]]) -> None:
        if denylist is None:
            return

        if self.allowlist is not None:
            raise ValueError("can't have both allowlist and denylist specified")

        for activity_name in denylist:
            self._validate_tool_activity(activity_name)

    def enable_activities(self) -> None:
        self.allowlist = None
        self.denylist = None

    def disable_activities(self) -> None:
        self.allowlist = []
        self.denylist = None

    # This method has to remain a method and can't be decorated with @property because
    # of the max depth recursion issue in `inspect.getmembers`.
    def activities(self) -> list[Callable]:
        methods = []

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            allowlist_condition = self.allowlist is None or name in self.allowlist
            denylist_condition = self.denylist is None or name not in self.denylist

            if getattr(method, "is_activity", False) and allowlist_condition and denylist_condition:
                methods.append(method)

        return methods

    def find_activity(self, name: str) -> Optional[Callable]:
        for method in self.activities():
            if getattr(method, "is_activity", False) and method.name == name:
                return method

        return None

    def activity_name(self, activity: Callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        else:
            return activity.name

    def activity_description(self, activity: Callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        else:
            return Template(activity.config["description"]).render({"_self": self})

    def activity_schema(self, activity: Callable) -> Optional[dict]:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        elif activity.config["schema"]:
            full_schema = {"values": activity.config["schema"].schema if activity.config["schema"] else {}}

            return Schema(full_schema).json_schema("InputSchema")
        else:
            return None

    def _validate_tool_activity(self, activity_name):
        tool = self.__class__

        activity = getattr(tool, activity_name, None)

        if not activity or not getattr(activity, "is_activity", False):
            raise ValueError(f"activity {activity_name} is not a valid activity for {tool}")
