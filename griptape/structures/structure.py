from __future__ import annotations
import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, TYPE_CHECKING, Any
from attr import define, field, Factory
from rich.logging import RichHandler
from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.drivers.embedding.openai_embedding_driver import OpenAiEmbeddingDriver, BaseEmbeddingDriver
from griptape.events.finish_structure_run_event import FinishStructureRunEvent
from griptape.events.start_structure_run_event import StartStructureRunEvent
from griptape.memory.meta import MetaMemory
from griptape.memory.structure import ConversationMemory
from griptape.memory import TaskMemory
from griptape.memory.task.storage import BlobArtifactStorage, TextArtifactStorage
from griptape.rules import Ruleset, Rule
from griptape.events import BaseEvent
from griptape.tokenizers import OpenAiTokenizer
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
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
            lambda self: OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL, stream=self.stream),
            takes_self=True,
        ),
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(default=Factory(lambda: OpenAiEmbeddingDriver()), kw_only=True)
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    custom_logger: Logger | None = field(default=None, kw_only=True)
    logger_level: int = field(default=logging.INFO, kw_only=True)
    event_listeners: list[EventListener] = field(factory=list, kw_only=True)
    conversation_memory: ConversationMemory | None = field(default=Factory(lambda: ConversationMemory()), kw_only=True)
    task_memory: TaskMemory | None = field(
        default=Factory(lambda self: self.default_task_memory, takes_self=True), kw_only=True
    )
    meta_memory: MetaMemory | None = field(default=Factory(lambda: MetaMemory()), kw_only=True)
    _execution_args: tuple = ()
    _logger: Logger | None = None

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
        if self.conversation_memory:
            self.conversation_memory.structure = self

        tasks = self.tasks.copy()
        self.tasks.clear()
        self.add_tasks(*tasks)
        self.prompt_driver.structure = self

    def __add__(self, other: BaseTask | list[BaseTask]) -> list[BaseTask]:
        return self.add_tasks(*other) if isinstance(other, list) else self + [other]

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

                self._logger.handlers = [RichHandler(show_time=True, show_path=False)]
            return self._logger

    @property
    def input_task(self) -> BaseTask | None:
        return self.tasks[0] if self.tasks else None

    @property
    def output_task(self) -> BaseTask | None:
        return self.tasks[-1] if self.tasks else None

    @property
    def finished_tasks(self) -> list[BaseTask]:
        return [s for s in self.tasks if s.is_finished()]

    @property
    def default_task_memory(self) -> TaskMemory:
        return TaskMemory(
            artifact_storages={
                TextArtifact: TextArtifactStorage(
                    query_engine=VectorQueryEngine(
                        prompt_driver=self.prompt_driver,
                        vector_store_driver=LocalVectorStoreDriver(embedding_driver=self.embedding_driver),
                    ),
                    summary_engine=PromptSummaryEngine(prompt_driver=self.prompt_driver),
                    csv_extraction_engine=CsvExtractionEngine(prompt_driver=self.prompt_driver),
                    json_extraction_engine=JsonExtractionEngine(prompt_driver=self.prompt_driver),
                ),
                BlobArtifact: BlobArtifactStorage(),
            }
        )

    def is_finished(self) -> bool:
        return all(s.is_finished() for s in self.tasks)

    def is_executing(self) -> bool:
        return any(s for s in self.tasks if s.is_executing())

    def find_task(self, task_id: str) -> BaseTask:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task with id {task_id} doesn't exist.")

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        return [self.add_task(s) for s in tasks]

    def add_event_listener(self, event_listener: EventListener) -> EventListener:
        if event_listener not in self.event_listeners:
            self.event_listeners.append(event_listener)

        return event_listener

    def remove_event_listener(self, event_listener: EventListener) -> None:
        if event_listener in self.event_listeners:
            self.event_listeners.remove(event_listener)
        else:
            raise ValueError(f"Event Listener not found.")

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

    def run(self, *args) -> Structure:
        self.before_run()

        result = self.try_run(*args)

        self.after_run()

        return result

    @abstractmethod
    def try_run(self, *args) -> Structure:
        ...
