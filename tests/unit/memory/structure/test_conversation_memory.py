import json
from griptape.structures import Agent
from griptape.utils import PromptStack
from griptape.memory.structure import ConversationMemory, Run, BaseConversationMemory
from griptape.structures import Pipeline
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tokenizer import MockTokenizer
from griptape.tasks import PromptTask


class TestConversationMemory:
    def test_add_run(self):
        memory = ConversationMemory()
        run = Run(input="test", output="test")

        memory.add_run(run)

        assert memory.runs[0] == run

    def test_to_json(self):
        memory = ConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert json.loads(memory.to_json())["type"] == "ConversationMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"] == "foo"

    def test_to_dict(self):
        memory = ConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert memory.to_dict()["type"] == "ConversationMemory"
        assert memory.to_dict()["runs"][0]["input"] == "foo"

    def test_to_prompt_stack(self):
        memory = ConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        prompt_stack = memory.to_prompt_stack()

        assert prompt_stack.inputs[0].content == "foo"
        assert prompt_stack.inputs[1].content == "bar"

    def test_from_dict(self):
        memory = ConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(BaseConversationMemory.from_dict(memory_dict), ConversationMemory)
        assert BaseConversationMemory.from_dict(memory_dict).runs[0].input == "foo"

    def test_from_json(self):
        memory = ConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), ConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"

    def test_buffering(self):
        memory = ConversationMemory(max_runs=2)

        pipeline = Pipeline(conversation_memory=memory, prompt_driver=MockPromptDriver())

        pipeline.add_tasks(PromptTask())

        pipeline.run("run1")
        pipeline.run("run2")
        pipeline.run("run3")
        pipeline.run("run4")
        pipeline.run("run5")

        assert len(pipeline.conversation_memory.runs) == 2
        assert pipeline.conversation_memory.runs[0].input == "run4"
        assert pipeline.conversation_memory.runs[1].input == "run5"

    def test_add_to_prompt_stack_autopruing_disabled(self):
        agent = Agent(prompt_driver=MockPromptDriver())
        memory = ConversationMemory(
            autoprune=False,
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
        prompt_stack.add_user_input("foo")
        prompt_stack.add_assistant_input("bar")
        memory.add_to_prompt_stack(prompt_stack)

        assert len(prompt_stack.inputs) == 12

    def test_add_to_prompt_stack_autopruning_enabled(self):
        # All memory is pruned.
        agent = Agent(prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_input_tokens=0)))
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
        memory.add_to_prompt_stack(prompt_stack)

        assert len(prompt_stack.inputs) == 3

        # No memory is pruned.
        agent = Agent(prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_input_tokens=1000)))
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
        memory.add_to_prompt_stack(prompt_stack)

        assert len(prompt_stack.inputs) == 13

        # One memory is pruned.
        # MockTokenizer's max_input_tokens set to one below the sum of memory + system prompt tokens
        # so that a single memory is pruned.
        agent = Agent(prompt_driver=MockPromptDriver(tokenizer=MockTokenizer(model="foo", max_input_tokens=160)))
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
        memory.add_to_prompt_stack(prompt_stack, 1)

        # We expect one run (2 prompt stack inputs) to be pruned.
        assert len(prompt_stack.inputs) == 11
        assert prompt_stack.inputs[0].content == "fizz"
        assert prompt_stack.inputs[1].content == "foo2"
        assert prompt_stack.inputs[2].content == "bar2"
        assert prompt_stack.inputs[-2].content == "foo"
        assert prompt_stack.inputs[-1].content == "bar"
