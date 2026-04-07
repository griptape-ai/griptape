import json

from griptape.artifacts import TextArtifact
from griptape.common import PromptStack
from griptape.memory.structure import BaseConversationMemory, ConversationMemory, Run
from griptape.structures import Agent, Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tokenizer import MockTokenizer


class TestConversationMemory:
    def test_add_run(self):
        memory = ConversationMemory()
        run = Run(input=TextArtifact("foo"), output=TextArtifact("bar"))

        memory.add_run(run)

        assert memory.runs[0] == run

    def test_to_json(self):
        memory = ConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        assert json.loads(memory.to_json())["type"] == "ConversationMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"]["value"] == "foo"

    def test_to_dict(self):
        memory = ConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        assert memory.to_dict()["type"] == "ConversationMemory"
        assert memory.to_dict()["runs"][0]["input"]["value"] == "foo"

    def test_to_prompt_stack(self):
        memory = ConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        prompt_stack = memory.to_prompt_stack()

        assert prompt_stack.messages[0].content[0].artifact.value == "foo"
        assert prompt_stack.messages[1].content[0].artifact.value == "bar"

    def test_from_dict(self):
        memory = ConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))
        memory_dict = memory.to_dict()

        assert isinstance(BaseConversationMemory.from_dict(memory_dict), ConversationMemory)
        assert BaseConversationMemory.from_dict(memory_dict).runs[0].input.value == "foo"

    def test_from_json(self):
        memory = ConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), ConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input.value == "foo"

    def test_buffering(self):
        memory = ConversationMemory(max_runs=2)

        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_tasks(PromptTask())

        pipeline.run("run1")
        pipeline.run("run2")
        pipeline.run("run3")
        pipeline.run("run4")
        pipeline.run("run5")

        assert len(pipeline.conversation_memory.runs) == 2
        assert pipeline.conversation_memory.runs[0].input.value == "run4"
        assert pipeline.conversation_memory.runs[1].input.value == "run5"

    def test_add_to_prompt_stack_autopruing_disabled(self):
        agent = Agent()
        memory = ConversationMemory(
            autoprune=False,
            runs=[
                Run(input=TextArtifact("foo1"), output=TextArtifact("bar1")),
                Run(input=TextArtifact("foo2"), output=TextArtifact("bar2")),
                Run(input=TextArtifact("foo3"), output=TextArtifact("bar3")),
                Run(input=TextArtifact("foo4"), output=TextArtifact("bar4")),
                Run(input=TextArtifact("foo5"), output=TextArtifact("bar5")),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(TextArtifact("foo"))
        prompt_stack.add_assistant_message("bar")
        memory.add_to_prompt_stack(agent.prompt_driver, prompt_stack)

        assert len(prompt_stack.messages) == 12

    def test_add_to_prompt_stack_autopruning_enabled(self, mock_config):
        # All memory is pruned.

        mock_config.drivers_config.prompt_driver = MockPromptDriver(
            tokenizer=MockTokenizer(model="foo", max_input_tokens=0)
        )
        agent = Agent()
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                Run(input=TextArtifact("foo1"), output=TextArtifact("bar1")),
                Run(input=TextArtifact("foo2"), output=TextArtifact("bar2")),
                Run(input=TextArtifact("foo3"), output=TextArtifact("bar3")),
                Run(input=TextArtifact("foo4"), output=TextArtifact("bar4")),
                Run(input=TextArtifact("foo5"), output=TextArtifact("bar5")),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("fizz")
        prompt_stack.add_user_message("foo")
        prompt_stack.add_assistant_message("bar")
        memory.add_to_prompt_stack(agent.prompt_driver, prompt_stack)

        assert len(prompt_stack.messages) == 3

        # No memory is pruned.
        mock_config.drivers_config.prompt_driver = MockPromptDriver(
            tokenizer=MockTokenizer(model="foo", max_input_tokens=1000)
        )
        agent = Agent()
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                Run(input=TextArtifact("foo1"), output=TextArtifact("bar1")),
                Run(input=TextArtifact("foo2"), output=TextArtifact("bar2")),
                Run(input=TextArtifact("foo3"), output=TextArtifact("bar3")),
                Run(input=TextArtifact("foo4"), output=TextArtifact("bar4")),
                Run(input=TextArtifact("foo5"), output=TextArtifact("bar5")),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("fizz")
        prompt_stack.add_user_message("foo")
        prompt_stack.add_assistant_message("bar")
        memory.add_to_prompt_stack(agent.prompt_driver, prompt_stack)

        assert len(prompt_stack.messages) == 13

        # One memory is pruned.
        # MockTokenizer's max_input_tokens set to one below the sum of memory + system prompt tokens
        # so that a single memory is pruned.
        mock_config.drivers_config.prompt_driver = MockPromptDriver(
            tokenizer=MockTokenizer(model="foo", max_input_tokens=160)
        )
        agent = Agent()
        memory = ConversationMemory(
            autoprune=True,
            runs=[
                # All of these sum to 155 tokens with the MockTokenizer.
                Run(input=TextArtifact("foo1"), output=TextArtifact("bar1")),
                Run(input=TextArtifact("foo2"), output=TextArtifact("bar2")),
                Run(input=TextArtifact("foo3"), output=TextArtifact("bar3")),
                Run(input=TextArtifact("foo4"), output=TextArtifact("bar4")),
                Run(input=TextArtifact("foo5"), output=TextArtifact("bar5")),
            ],
        )
        memory.structure = agent
        prompt_stack = PromptStack()
        # And then another 6 tokens from fizz for a total of 161 tokens.
        prompt_stack.add_system_message("fizz")
        prompt_stack.add_user_message("foo")
        prompt_stack.add_assistant_message("bar")
        memory.add_to_prompt_stack(agent.prompt_driver, prompt_stack, 1)

        # We expect one run (2 Prompt Stack inputs) to be pruned.
        assert len(prompt_stack.messages) == 11
        assert prompt_stack.messages[0].content[0].artifact.value == "fizz"
        assert prompt_stack.messages[1].content[0].artifact.value == "foo2"
        assert prompt_stack.messages[2].content[0].artifact.value == "bar2"
        assert prompt_stack.messages[-2].content[0].artifact.value == "foo"
        assert prompt_stack.messages[-1].content[0].artifact.value == "bar"
