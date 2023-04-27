import inspect
from typing import Optional
from jinja2 import Template


class ActivityMixin:
    @property
    def schema_template_args(self) -> dict:
        return {}

    def activities(self) -> list[callable]:
        methods = []

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "is_activity", False):
                methods.append(method)

        return methods

    def find_activity(self, name: str) -> Optional[callable]:
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, "is_activity", False) and method.config["name"] == name:
                return method

        return None

    def activity_name(self, activity: callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not a tool activity.")
        else:
            return activity.config["name"]

    def activity_description(self, activity: callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not a tool activity.")
        else:
            return Template(activity.config["description"]).render(self.schema_template_args)

    def full_activity_description(self, activity: callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not a tool activity.")
        else:
            description_lines = [
                self.activity_description(activity),
                f"Method input schema: {self.activity_schema(activity)}"
            ]

            return str.join("\n", description_lines)

    def activity_schema(self, activity: callable) -> dict:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not a tool activity.")
        else:
            return activity.config["schema"].json_schema("ToolInputSchema")