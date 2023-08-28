from datetime import datetime
from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class DateTime(BaseTool):
    @activity(config={
        "uses_default_memory": False,
        "description": "Can be used to return current date and time. Always use it when you need to know what the "
                       "current date or time is."
    })
    def get_current_datetime(self, _: dict) -> BaseArtifact:
        try:
            current_datetime = datetime.now()

            return TextArtifact(str(current_datetime))
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")
