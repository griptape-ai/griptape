from __future__ import annotations
from collections.abc import Iterator
from attr import define, field
from griptape.utils import PromptStack
from griptape.artifacts.action_chunk_artifact import ActionChunkArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer
from griptape.artifacts import TextArtifact, ActionsArtifact
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_output: str = field(default="mock output", kw_only=True)
    mock_tool_input: str = field(default="mock input", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        if prompt_stack.tools:
            actions = [
                ActionsArtifact.Action(
                    tag=f"{tool.activity_name(activity)}-id",
                    name=tool.name,
                    path=tool.activity_name(activity),
                    input={"values": self.mock_tool_input},
                )
                for tool in prompt_stack.tools
                for activity in tool.activities()
            ]

            return ActionsArtifact(value=self.mock_output, actions=actions)
        else:
            return TextArtifact(value=self.mock_output)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact | ActionChunkArtifact]:
        if prompt_stack.tools:
            actions = [
                ActionsArtifact.Action(
                    tag=f"{tool.activity_name(activity)}-id",
                    name=tool.name,
                    path=tool.activity_name(activity),
                    input={"values": self.mock_tool_input},
                )
                for tool in prompt_stack.tools
                for activity in tool.activities()
            ]

            for index, action in enumerate(actions):
                yield ActionChunkArtifact(
                    value=self.mock_output, tag=action.tag, name=action.name, path=action.path, index=index
                )
                yield ActionChunkArtifact(value=self.mock_output, index=index, partial_input=self.mock_tool_input)
        else:
            yield TextArtifact(value=self.mock_output)
