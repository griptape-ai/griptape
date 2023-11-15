import pytest
from dataclasses import dataclass, field
from typing import List, Any
from unittest.mock import Mock
from griptape.utils import PromptStack
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tokenizer import MockTokenizer
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.structures.agent import Agent
from griptape.memory.structure import ConversationMemory, Run
from griptape.processors.base_processors import BasePromptStackProcessor


class MockPromptStackProcessor(BasePromptStackProcessor):
    def before_run(self, prompt: str) -> None:
        pass

    def after_run(self, result: Any) -> Any:
        return result


class TestPromptStack:
    @pytest.fixture
    def prompt_stack(self) -> PromptStack:
        processor = MockPromptStackProcessor()
        processor.before_run = Mock()
        processor.after_run = Mock()
        return PromptStack(prompt_stack_processors=[processor])

    def test_init(self) -> None:
        assert PromptStack(prompt_stack_processors=[MockPromptStackProcessor()])

    def test_add_input(self, prompt_stack: PromptStack) -> None:
        prompt_stack.add_input("foo", "role")
        assert prompt_stack.inputs[0].role == "role"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_generic_input(self, prompt_stack: PromptStack) -> None:
        prompt_stack.add_generic_input("foo")
        assert prompt_stack.inputs[0].role == "generic"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_system_input(self, prompt_stack: PromptStack) -> None:
        prompt_stack.add_system_input("foo")
        assert prompt_stack.inputs[0].role == "system"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_user_input(self, prompt_stack: PromptStack) -> None:
        prompt_stack.add_user_input("foo")
        assert prompt_stack.inputs[0].role == "user"
        assert prompt_stack.inputs[0].content == "foo"

    def test_add_assistant_input(self, prompt_stack: PromptStack) -> None:
        prompt_stack.add_assistant_input("foo")
        assert prompt_stack.inputs[0].role == "assistant"
        assert prompt_stack.inputs[0].content == "foo"

    def test_before_run(self, prompt_stack: PromptStack) -> None:
        prompt_stack.before_run("test prompt")
        assert prompt_stack.prompt_stack_processors[0].before_run.called

    def test_after_run(self, prompt_stack: PromptStack) -> None:
        prompt_stack.after_run("test result")
        assert prompt_stack.prompt_stack_processors[0].after_run.called

    def test_add_conversation_memory_autopruing_enabled(self) -> None:
        # All memory is pruned.
        agent = Agent(
            prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_tokens=0)),
            embedding_driver=MockEmbeddingDriver(),
        )
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                Run(input="foo1", output="bar1"),
                Run(input="foo2", output="bar2"),
                Run(input="foo3", output="bar3"),
                Run(input="foo4", output="bar4"),
                Run(input="foo5", output="bar5"),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        prompt_stack.add_system_input("fizz")
        prompt_stack.add_user_input("foo")
        prompt_stack.add_assistant_input("bar")
        prompt_stack.add_conversation_memory(memory)
        assert len(prompt_stack.inputs) == 3

        # No memory is pruned.
        agent = Agent(
            prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_tokens=1000)),
            embedding_driver=MockEmbeddingDriver(),
        )
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                Run(input="foo1", output="bar1"),
                Run(input="foo2", output="bar2"),
                Run(input="foo3", output="bar3"),
                Run(input="foo4", output="bar4"),
                Run(input="foo5", output="bar5"),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        prompt_stack.add_system_input("fizz")
        prompt_stack.add_user_input("foo")
        prompt_stack.add_assistant_input("bar")
        prompt_stack.add_conversation_memory(memory)
        assert len(prompt_stack.inputs) == 13

        # One memory is pruned.
        # MockTokenizer's max_tokens set to one below the sum of memory + system prompt tokens
        # so that a single memory is pruned.
        agent = Agent(
            prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_tokens=160)),
            embedding_driver=MockEmbeddingDriver(),
        )
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                # All of these sum to 155 tokens with the MockTokenizer.
                Run(input="foo1", output="bar1"),
                Run(input="foo2", output="bar2"),
                Run(input="foo3", output="bar3"),
                Run(input="foo4", output="bar4"),
                Run(input="foo5", output="bar5"),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        # And then another 6 tokens from fizz for a total of 161 tokens.
        prompt_stack.add_system_input("fizz")
        prompt_stack.add_user_input("foo")
        prompt_stack.add_assistant_input("bar")
        prompt_stack.add_conversation_memory(memory, 1)

        # We expect one run (2 prompt stack inputs) to be pruned.
        assert len(prompt_stack.inputs) == 11
        assert prompt_stack.inputs[0].content == "fizz"
        assert prompt_stack.inputs[1].content == "foo2"
        assert prompt_stack.inputs[2].content == "bar2"
        assert prompt_stack.inputs[-2].content == "foo"
        assert prompt_stack.inputs[-1].content == "bar"
