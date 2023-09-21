from datetime import datetime
from dateparser import parse
from schema import Schema, Literal
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class DateTime(BaseTool):
    @activity(config={
        "uses_default_memory": False,
        "description": "Can be used to return current date and time."
    })
    def get_current_datetime(self, _: dict) -> BaseArtifact:
        try:
            current_datetime = datetime.now()

            return TextArtifact(str(current_datetime))
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")
    
    @activity(config={
        "uses_default_memory": False,
        "description": "Can be used to return a relative date and time.",
        "schema": Schema({
            Literal(
                "relative_date_string",
                description='Relative date in English. For example, "now EST", "20 minutes ago", or "yesterday at 2pm"'
            ): str
        })
    })
    def get_relative_datetime(self, params: dict) -> BaseArtifact:
        try:
            date_string = params["values"]["relative_date_string"]
            relative_datetime = parse(date_string)

            return TextArtifact(str(relative_datetime))
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")
