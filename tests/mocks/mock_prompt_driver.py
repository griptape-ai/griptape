from __future__ import annotations

import json
from collections.abc import Iterator

from attr import define, field

from griptape.artifacts import ActionsArtifact, TextArtifact, ActionArtifact, TextChunkArtifact
from griptape.artifacts.action_chunk_artifact import ActionChunkArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer
from griptape.utils import PromptStack
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_output: str = field(default="mock output", kw_only=True)
    mock_thought: str = field(default="mock thought", kw_only=True)
    mock_tool_input: str = field(default='{"values": {"test": "mock tool input"}}', kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        if self.use_native_tools:
            if prompt_stack.tools and prompt_stack.inputs and prompt_stack.inputs[-1].role == PromptStack.USER_ROLE:
                actions = [
                    ActionArtifact.Action(
                        tag=f"{tool.activity_name(activity)}-id",
                        name=tool.name,
                        path=tool.activity_name(activity),
                        input=json.loads(self.mock_tool_input),
                        output=TextArtifact(value=self.mock_output),
                    )
                    for tool in prompt_stack.tools
                    for activity in tool.activities()
                ]

                return ActionsArtifact(value=self.mock_thought, actions=actions)
            else:
                return TextArtifact(value=f"Answer: {self.mock_output}")
        else:
            return TextArtifact(value=self.mock_output)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextChunkArtifact | ActionChunkArtifact]:
        if self.use_native_tools:
            if prompt_stack.tools and prompt_stack.inputs and prompt_stack.inputs[-1].role == PromptStack.USER_ROLE:
                actions = [
                    ActionArtifact.Action(
                        tag=f"{tool.activity_name(activity)}-id",
                        name=tool.name,
                        path=tool.activity_name(activity),
                        output=TextArtifact(value=self.mock_output),
                    )
                    for tool in prompt_stack.tools
                    for activity in tool.activities()
                ]

                yield TextChunkArtifact(value=self.mock_thought)
                for index, action in enumerate(actions):
                    yield ActionChunkArtifact(
                        value=ActionChunkArtifact.ActionChunk(
                            tag=action.tag, name=action.name, path=action.path, index=index
                        )
                    )
                    yield ActionChunkArtifact(
                        value=ActionChunkArtifact.ActionChunk(index=index, input=self.mock_tool_input)
                    )
            else:
                yield TextChunkArtifact(value=f"Answer: {self.mock_output}")
        else:
            yield TextChunkArtifact(value=self.mock_output)
