class TestToolOverview:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/tools/
    """

    def test_tool_overview(self):
        from griptape.structures import Agent
        from griptape.events import (
            BaseEvent,
            StartTaskEvent,
            FinishTaskEvent,
            StartSubtaskEvent,
            FinishSubtaskEvent,
            StartPromptEvent,
            FinishPromptEvent,
        )

        def handler(event: BaseEvent):
            print(event)

        agent = Agent(
            event_listeners={
                StartTaskEvent: [handler],
                FinishTaskEvent: [handler],
                StartSubtaskEvent: [handler],
                FinishSubtaskEvent: [handler],
                StartPromptEvent: [handler],
                FinishPromptEvent: [handler],
            }
        )

        result = agent.run("tell me about griptape")

        assert result.output is not None

    def test_events_multiple_handlers(self):
        from griptape.structures import Agent
        from griptape.events import BaseEvent

        def handler1(event: BaseEvent):
            print(event)

        def handler2(event: BaseEvent):
            print(event)

        agent = Agent(event_listeners=[handler1, handler2])

        result = agent.run("tell me about griptape")

        assert result.output is not None
