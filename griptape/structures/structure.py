from __future__ import annotations
import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, TYPE_CHECKING, Callable, Type, Any, Tuple
from attr import define, field, Factory
from rich.logging import RichHandler
from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.drivers.embedding.openai_embedding_driver import (
    OpenAiEmbeddingDriver,
    BaseEmbeddingDriver,
)
from griptape.events.finish_structure_run_event import FinishStructureRunEvent
from griptape.events.start_structure_run_event import StartStructureRunEvent
from griptape.memory.structure import ConversationMemory
from griptape.memory import ToolMemory
from griptape.memory.tool.storage import (
    BlobArtifactStorage,
    TextArtifactStorage,
)
from griptape.rules import Ruleset, Rule
from griptape.events import BaseEvent
from griptape.tokenizers import OpenAiTokenizer
from griptape.engines import (
    VectorQueryEngine,
    PromptSummaryEngine,
    CsvExtractionEngine,
    JsonExtractionEngine,
)
from griptape.drivers import LocalVectorStoreDriver
from griptape.events import EventListener

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Structure(ABC):
    LOGGER_NAME = "griptape"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    stream: bool = field(default=False, kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: OpenAiChatPromptDriver(
                model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL,
                stream=self.stream,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver()), kw_only=True
    )
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    custom_logger: Optional[Logger] = field(default=None, kw_only=True)
    logger_level: int = field(default=logging.INFO, kw_only=True)
    event_listeners: list[EventListener] = field(factory=list, kw_only=True)
    memory: Optional[ConversationMemory] = field(default=None, kw_only=True)
    tool_memory: Optional[ToolMemory] = field(
        default=Factory(
            lambda self: ToolMemory(
                artifact_storages={
                    TextArtifact: TextArtifactStorage(
                        query_engine=VectorQueryEngine(
                            prompt_driver=self.prompt_driver,
                            vector_store_driver=LocalVectorStoreDriver(
                                embedding_driver=self.embedding_driver
                            ),
                        ),
                        summary_engine=PromptSummaryEngine(
                            prompt_driver=self.prompt_driver
                        ),
                        csv_extraction_engine=CsvExtractionEngine(
                            prompt_driver=self.prompt_driver
                        ),
                        json_extraction_engine=JsonExtractionEngine(
                            prompt_driver=self.prompt_driver
                        ),
                    ),
                    BlobArtifact: BlobArtifactStorage(),
                }
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    _execution_args: tuple = ()
    _logger: Optional[Logger] = None

    @tasks.validator
    def validate_tasks(self, _, tasks: list[BaseTask]) -> None:
        if len(tasks) > 0:
            raise ValueError(
                "Tasks can't be initialized directly. Use add_task or add_tasks method instead"
            )

    @rulesets.validator
    def validate_rulesets(self, _, rulesets: list[Ruleset]) -> None:
        if not rulesets:
            return

        if self.rules:
            raise ValueError("can't have both rulesets and rules specified")

    @rules.validator
    def validate_rules(self, _, rules: list[Rule]) -> None:
        if not rules:
            return

        if self.rulesets:
            raise ValueError("can't have both rules and rulesets specified")

    def __attrs_post_init__(self) -> None:
        if self.memory:
            self.memory.structure = self

        [task.preprocess(self) for task in self.tasks]

        self.prompt_driver.structure = self

    @property
    def execution_args(self) -> tuple:
        return self._execution_args

    @property
    def logger(self) -> Logger:
        if self.custom_logger:
            return self.custom_logger
        else:
            if self._logger is None:
                self._logger = logging.getLogger(self.LOGGER_NAME)

                self._logger.propagate = False
                self._logger.level = self.logger_level

                self._logger.handlers = [
                    RichHandler(show_time=True, show_path=False)
                ]
            return self._logger

    def is_finished(self) -> bool:
        return all(s.is_finished() for s in self.tasks)

    def is_executing(self) -> bool:
        return any(s for s in self.tasks if s.is_executing())

    def find_task(self, task_id: str) -> Optional[BaseTask]:
        return next((task for task in self.tasks if task.id == task_id), None)

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        return [self.add_task(s) for s in tasks]

    def add_event_listener(
        self,
        handler: Callable[[BaseEvent], Any],
        event_types: Optional[list[Type[BaseEvent]]] = None,
    ) -> None:
        event_listener = EventListener(handler, event_types=event_types)

        if event_listener not in self.event_listeners:
            self.event_listeners.append(event_listener)

    def publish_event(self, event: BaseEvent) -> None:
        for event_listener in self.event_listeners:
            handler = event_listener.handler
            event_types = event_listener.event_types

            if event_types is None or type(event) in event_types:
                handler(event)

    def context(self, task: BaseTask) -> dict[str, Any]:
        return {"args": self.execution_args, "structure": self}

    def before_run(self) -> None:
        self.publish_event(StartStructureRunEvent())

    def after_run(self) -> None:
        self.publish_event(FinishStructureRunEvent())

    @abstractmethod
    def add_task(self, task: BaseTask) -> BaseTask:
        ...

    def run(self, *args) -> BaseTask | list[BaseTask]:
        self.before_run()

        result = self.try_run(*args)

        self.after_run()

        return result

    @abstractmethod
    def try_run(self, *args) -> BaseTask | list[BaseTask]:
        ...
