from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.common import DeltaMessage, PromptStack
from tests.mocks.mock_prompt_driver import MockPromptDriver

if TYPE_CHECKING:
    from collections.abc import Iterator


@define
class MockStreamUsagePromptDriver(MockPromptDriver):
    """Emits a fixed sequence of usage-only deltas from try_stream.

    Mimics providers that report usage as running totals over the stream rather than
    per-delta increments (Anthropic's cumulative ``message_delta`` usage, Gemini's
    per-chunk ``usage_metadata``).
    """

    stream_usage_deltas: list[DeltaMessage.Usage] = field(factory=list, kw_only=True)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        for usage in self.stream_usage_deltas:
            yield DeltaMessage(usage=usage)
