import langchain.tools
from attr import define
from griptape.core import BaseAdapter


@define
class LangchainToolAdapter(BaseAdapter):
    def generate_tool(self, tool_action: callable) -> langchain.tools.BaseTool:
        tool = tool_action.__self__

        # Double up curly brackets for correct f-string parsing in LangChain prompt templates.
        description = tool.action_description(tool_action).replace("{", "{{").replace("}", "}}")

        def _run(_self, value: str) -> str:
            return self.executor.execute(tool_action, value.encode()).decode()

        async def _arun(_self, query: str) -> str:
            raise NotImplementedError("async is not supported")

        return type(
            f"Griptape{tool.__class__.__name__}Tool",
            (langchain.tools.BaseTool,),
            {
                "name": tool_action.config["name"],
                "description": description,
                "_run": _run,
                "_arun": _arun
            }
        )()
