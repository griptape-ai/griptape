from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field
from typing_extensions import override

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers.assistant import BaseAssistantDriver
from griptape.events import EventBus, TextChunkEvent
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import openai
    from openai import AssistantEventHandler
    from openai.types.beta.threads import Text, TextDelta
    from openai.types.beta.threads.runs import ToolCall, ToolCallDelta


@define
class OpenAiAssistantDriver(BaseAssistantDriver):
    @staticmethod
    def _create_event_handler_class() -> type[AssistantEventHandler]:  # pyright: ignore[reportInvalidTypeForm]
        """Lazily import and create EventHandler class."""
        AssistantEventHandler = import_optional_dependency("openai").AssistantEventHandler  # noqa: N806

        class EventHandler(AssistantEventHandler):
            @override
            def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:  # pyright: ignore[reportGeneralTypeIssues,reportUndefinedVariable] Pyright can't verify override since base class is in TYPE_CHECKING
                if delta.value is not None:
                    EventBus.publish_event(TextChunkEvent(token=delta.value))

            @override
            def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None:  # pyright: ignore[reportGeneralTypeIssues,reportUndefinedVariable] Pyright can't verify override since base class is in TYPE_CHECKING
                if delta.type == "code_interpreter" and delta.code_interpreter is not None:
                    if delta.code_interpreter.input:
                        EventBus.publish_event(TextChunkEvent(token=delta.code_interpreter.input))
                    if delta.code_interpreter.outputs:
                        EventBus.publish_event(TextChunkEvent(token="\n\noutput >"))
                        for output in delta.code_interpreter.outputs:
                            if output.type == "logs" and output.logs:
                                EventBus.publish_event(TextChunkEvent(token=output.logs))

        return EventHandler

    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    thread_id: Optional[str] = field(default=None, kw_only=True)
    assistant_id: str = field(kw_only=True)
    event_handler: AssistantEventHandler = field(  # pyright: ignore[reportInvalidTypeForm]
        default=Factory(lambda self: self._create_event_handler_class()(), takes_self=True),
        kw_only=True,
        metadata={"serializable": False},
    )
    auto_create_thread: bool = field(default=True, kw_only=True)

    _client: Optional[openai.OpenAI] = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )

    @lazy_property()
    def client(self) -> openai.OpenAI:
        openai = import_optional_dependency("openai")
        return openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            organization=self.organization,
        )

    def try_run(self, *args: BaseArtifact) -> TextArtifact:
        if self.thread_id is None:
            if self.auto_create_thread:
                thread_id = self.client.beta.threads.create().id
                self.thread_id = thread_id
            else:
                raise ValueError("Thread ID is required but not provided and auto_create_thread is disabled.")
        else:
            thread_id = self.thread_id

        response = self._create_run(thread_id, *args)

        response.meta.update({"assistant_id": self.assistant_id, "thread_id": self.thread_id})

        return response

    def _create_run(self, thread_id: str, *args: BaseArtifact) -> TextArtifact:
        content = "\n".join(arg.value for arg in args)
        message_id = self.client.beta.threads.messages.create(thread_id=thread_id, role="user", content=content)
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            event_handler=self.event_handler,
        ) as stream:
            stream.until_done()
            last_messages = stream.get_final_messages()

            message_contents = []
            for message in last_messages:
                message_contents.append(
                    "".join(content.text.value for content in message.content if content.type == "TextContentBlock")
                )
            message_text = "\n".join(message_contents)

            response = TextArtifact(message_text)

            response.meta.update(
                {"assistant_id": self.assistant_id, "thread_id": self.thread_id, "message_id": message_id}
            )
            return response


# Lazy descriptor for EventHandler to avoid importing openai at module load time
class _EventHandlerDescriptor:
    """Descriptor that lazily creates and caches the EventHandler class.

    This provides backwards compatibility with tests that expect
    OpenAiAssistantDriver.EventHandler to be accessible, while keeping
    the openai SDK import lazy.
    """

    def __init__(self) -> None:
        self._handler_class = None

    def __get__(self, obj, objtype=None):  # noqa: ANN001, ANN204
        if self._handler_class is None:
            self._handler_class = OpenAiAssistantDriver._create_event_handler_class()
        return self._handler_class


# Dynamic attribute assignment is not recognized by pyright
OpenAiAssistantDriver.EventHandler = _EventHandlerDescriptor()  # pyright: ignore[reportAttributeAccessIssue]
