import langchain.tools
from attr import define

from griptape.artifacts import TextArtifact
from griptape.converters import BaseConverter


@define
class LangchainToolConverter(BaseConverter):
    def generate_tool(self, tool_activity: callable) -> langchain.tools.BaseTool:
        tool = tool_activity.__self__

        # Double up curly brackets for correct f-string parsing in LangChain prompt templates.
        description = tool.full_activity_description(tool_activity).replace("{", "{{").replace("}", "}}")

        def _run(_self, value: str) -> str:
            return self.executor.execute(tool_activity, TextArtifact(value)).value

        async def _arun(_self, value: str) -> str:
            raise NotImplementedError("async is not supported")

        return type(
            f"Griptape{tool.__class__.__name__}Tool",
            (langchain.tools.BaseTool,),
            {
                "name": tool_activity.config["name"],
                "description": description,
                "_run": _run,
                "_arun": _arun
            }
        )()
