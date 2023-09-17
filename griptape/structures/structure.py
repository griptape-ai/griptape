from __future__ import annotations
import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, Union, TYPE_CHECKING, Callable, Type
from attr import define, field, Factory
from rich.logging import RichHandler
from griptape.drivers import BasePromptDriver, OpenAiChatPromptDriver
from griptape.drivers.embedding.openai_embedding_driver import OpenAiEmbeddingDriver, BaseEmbeddingDriver
from griptape.memory.structure import ConversationMemory
from griptape.memory.tool import BaseToolMemory, TextToolMemory
from griptape.rules import Ruleset
from griptape.events import BaseEvent
from griptape.tokenizers import TiktokenTokenizer
from griptape.engines import VectorQueryEngine, PromptSummaryEngine
from griptape.drivers import LocalVectorStoreDriver

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Structure(ABC):
    LOGGER_NAME = "griptape"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiChatPromptDriver(
            model=TiktokenTokenizer.DEFAULT_OPENAI_GPT_4_MODEL
        )),
        kw_only=True
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: OpenAiEmbeddingDriver()),
        kw_only=True
    )
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    custom_logger: Optional[Logger] = field(default=None, kw_only=True)
    logger_level: int = field(default=logging.INFO, kw_only=True)
    event_listeners: Union[list[Callable], dict[Type[BaseEvent], list[Callable]]] = field(factory=list, kw_only=True)
    memory: Optional[ConversationMemory] = field(default=None, kw_only=True)
    tool_memory: Optional[BaseToolMemory] = field(
        default=Factory(lambda self: TextToolMemory(
            query_engine=VectorQueryEngine(
                vector_store_driver=LocalVectorStoreDriver(
                    embedding_driver=self.embedding_driver
                )
            ),
            summary_engine=PromptSummaryEngine()
        ), takes_self=True),
        kw_only=True
    )
    _execution_args: tuple = ()
    _logger: Optional[Logger] = None

    @tasks.validator
    def validate_tasks(self, _, tasks: list[BaseTask]) -> None:
        if len(tasks) > 0:
            raise ValueError("Tasks can't be initialized directly. Use add_task or add_tasks method instead")

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
                    RichHandler(
                        show_time=True,
                        show_path=False
                    )
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

    def publish_event(self, event: BaseEvent) -> None:
        if isinstance(self.event_listeners, dict):
            listeners = self.event_listeners.get(type(event), [])
        else:
            listeners = self.event_listeners

        for listener in listeners:
            listener(event)

    def context(self, task: BaseTask) -> dict[str, any]:
        return {
            "args": self.execution_args,
            "structure": self,
        }

    @abstractmethod
    def add_task(self, task: BaseTask) -> BaseTask:
        ...

    @abstractmethod
    def run(self, *args) -> Union[BaseTask, list[BaseTask]]:
        ...
