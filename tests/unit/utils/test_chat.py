from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent
from griptape.utils import Chat
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestConversation:
    def test_init(self):
        agent = Agent(prompt_driver=MockPromptDriver(), memory=ConversationMemory())

        assert Chat(agent).structure == agent
