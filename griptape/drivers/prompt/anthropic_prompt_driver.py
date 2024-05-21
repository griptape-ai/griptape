from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING
from collections.abc import Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack, import_optional_dependency
from griptape.artifacts import ActionsArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AnthropicTokenizer

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define
class AnthropicPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
        tokenizer: Custom `AnthropicTokenizer`.
    """

    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Any = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: AnthropicTokenizer = field(
        default=Factory(lambda self: AnthropicTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    top_p: float = field(default=0.999, kw_only=True, metadata={"serializable": True})
    top_k: int = field(default=250, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        response = self.client.beta.tools.messages.create(**self._base_params(prompt_stack))

        text = response.content[0].text if response.content and response.content[0].type == "text" else ""
        tool_uses = [content for content in response.content if content.type == "tool_use"]

        if tool_uses:
            actions = [
                ActionsArtifact.Action(
                    tag=tool_use.id,
                    name=tool_use.name.split("-")[0],
                    path=tool_use.name.split("-")[1],
                    input=tool_use.input,
                )
                for tool_use in tool_uses
            ]

            return ActionsArtifact(value=text, actions=actions)
        else:
            return TextArtifact(value=text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        response = self.client.beta.messages.create(**self._base_params(prompt_stack), stream=True)

        for chunk in response:
            if chunk.type == "content_block_delta":
                yield TextArtifact(value=chunk.delta.text)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> dict:
        messages = [
            {"role": self.__to_anthropic_role(prompt_input), "content": self.__to_anthropic_content(prompt_input)}
            for prompt_input in prompt_stack.inputs
            if not prompt_input.is_system()
        ]
        system = next((i for i in prompt_stack.inputs if i.is_system()), None)

        if system is None:
            return {"messages": messages}
        else:
            return {"messages": messages, "system": system.content}

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_output_tokens(self.prompt_stack_to_string(prompt_stack)),
            "top_p": self.top_p,
            "top_k": self.top_k,
            "tool_choice": {"type": "auto"},
            **(
                {"tools": self.__to_anthropic_tools(prompt_stack.tools)}
                if prompt_stack.tools and self.function_calling
                else {}
            ),
            **self._prompt_stack_to_messages(prompt_stack),
        }

    def __to_anthropic_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_anthropic_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "name": f"{tool.name}-{tool.activity_name(activity)}",
                "description": tool.activity_description(activity),
                "input_schema": tool.activity_schema(activity).json_schema("Action Schema"),
            }
            for tool in tools
            for activity in tool.activities()
        ]

    def __to_anthropic_content(self, input: PromptStack.Input) -> str | list[dict]:
        if input.is_tool_result():
            return [
                {"type": "tool_result", "tool_use_id": tool_call.tag, "content": input.content}
                for tool_call in input.tool_calls
            ]
        elif input.is_tool_call():
            return [
                {"type": "text", "text": input.content},
                *[
                    {
                        "type": "tool_use",
                        "id": tool_call.tag,
                        "name": f"{tool_call.name}-{tool_call.path}",
                        "input": tool_call.input,
                    }
                    for tool_call in input.tool_calls
                ],
            ]
        else:
            return input.content
