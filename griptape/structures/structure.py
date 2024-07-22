from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from logging import Logger
from typing import TYPE_CHECKING, Any, Optional

from attrs import Attribute, Factory, define, field
from rich.logging import RichHandler

from griptape.artifacts import BaseArtifact, BlobArtifact, TextArtifact
from griptape.common import observable
from griptape.config import BaseStructureConfig, OpenAiStructureConfig, StructureConfig
from griptape.drivers import (
    BaseEmbeddingDriver,
    BasePromptDriver,
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.engines import CsvExtractionEngine, JsonExtractionEngine, PromptSummaryEngine
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    MetadataBeforeResponseRagModule,
    PromptResponseRagModule,
    RulesetsBeforeResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.events.finish_structure_run_event import FinishStructureRunEvent
from griptape.events.start_structure_run_event import StartStructureRunEvent
from griptape.memory import TaskMemory
from griptape.memory.meta import MetaMemory
from griptape.memory.structure import ConversationMemory
from griptape.memory.task.storage import BlobArtifactStorage, TextArtifactStorage
from griptape.mixins import EventPublisherMixin
from griptape.utils import deprecation_warn

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory
    from griptape.rules import Rule, Ruleset
    from griptape.tasks import BaseTask


@define
class Structure(ABC, EventPublisherMixin):
    LOGGER_NAME = "griptape"

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    stream: Optional[bool] = field(default=None, kw_only=True)
    prompt_driver: Optional[BasePromptDriver] = field(default=None)
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    config: BaseStructureConfig = field(
        default=Factory(lambda self: self.default_config, takes_self=True),
        kw_only=True,
    )
    rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    rules: list[Rule] = field(factory=list, kw_only=True)
    tasks: list[BaseTask] = field(factory=list, kw_only=True)
    custom_logger: Optional[Logger] = field(default=None, kw_only=True)
    logger_level: int = field(default=logging.INFO, kw_only=True)
    conversation_memory: Optional[BaseConversationMemory] = field(
        default=Factory(
            lambda self: ConversationMemory(driver=self.config.conversation_memory_driver),
            takes_self=True,
        ),
        kw_only=True,
    )
    rag_engine: RagEngine = field(default=Factory(lambda self: self.default_rag_engine, takes_self=True), kw_only=True)
    task_memory: TaskMemory = field(
        default=Factory(lambda self: self.default_task_memory, takes_self=True),
        kw_only=True,
    )
    meta_memory: MetaMemory = field(default=Factory(lambda: MetaMemory()), kw_only=True)
    fail_fast: bool = field(default=True, kw_only=True)
    _execution_args: tuple = ()
    _logger: Optional[Logger] = None

    @rulesets.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_rulesets(self, _: Attribute, rulesets: list[Ruleset]) -> None:
        if not rulesets:
            return

        if self.rules:
            raise ValueError("can't have both rulesets and rules specified")

    @rules.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_rules(self, _: Attribute, rules: list[Rule]) -> None:
        if not rules:
            return

        if self.rulesets:
            raise ValueError("can't have both rules and rulesets specified")

    def __attrs_post_init__(self) -> None:
        if self.conversation_memory is not None:
            self.conversation_memory.structure = self

        self.config.structure = self

        tasks = self.tasks.copy()
        self.tasks.clear()
        self.add_tasks(*tasks)

    def __add__(self, other: BaseTask | list[BaseTask]) -> list[BaseTask]:
        return self.add_tasks(*other) if isinstance(other, list) else self + [other]

    @prompt_driver.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_prompt_driver(self, attribute: Attribute, value: BasePromptDriver) -> None:
        if value is not None:
            deprecation_warn(f"`{attribute.name}` is deprecated, use `config.prompt_driver` instead.")

    @embedding_driver.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_embedding_driver(self, attribute: Attribute, value: BaseEmbeddingDriver) -> None:
        if value is not None:
            deprecation_warn(f"`{attribute.name}` is deprecated, use `config.embedding_driver` instead.")

    @stream.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_stream(self, attribute: Attribute, value: bool) -> None:  # noqa: FBT001
        if value is not None:
            deprecation_warn(f"`{attribute.name}` is deprecated, use `config.prompt_driver.stream` instead.")

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
    def input_task(self) -> Optional[BaseTask]:
        return self.tasks[0] if self.tasks else None

    @property
    def output_task(self) -> Optional[BaseTask]:
        return self.tasks[-1] if self.tasks else None

    @property
    def output(self) -> Optional[BaseArtifact]:
        return self.output_task.output if self.output_task is not None else None

    @property
    def finished_tasks(self) -> list[BaseTask]:
        return [s for s in self.tasks if s.is_finished()]

    @property
    def default_config(self) -> BaseStructureConfig:
        if self.prompt_driver is not None or self.embedding_driver is not None or self.stream is not None:
            config = StructureConfig()

            prompt_driver = OpenAiChatPromptDriver(model="gpt-4o") if self.prompt_driver is None else self.prompt_driver

            embedding_driver = OpenAiEmbeddingDriver() if self.embedding_driver is None else self.embedding_driver

            if self.stream is not None:
                prompt_driver.stream = self.stream

            vector_store_driver = LocalVectorStoreDriver(embedding_driver=embedding_driver)

            config.prompt_driver = prompt_driver
            config.vector_store_driver = vector_store_driver
            config.embedding_driver = embedding_driver
        else:
            config = OpenAiStructureConfig()

        return config

    @property
    def default_rag_engine(self) -> RagEngine:
        return RagEngine(
            retrieval_stage=RetrievalRagStage(
                retrieval_modules=[VectorStoreRetrievalRagModule(vector_store_driver=self.config.vector_store_driver)],
            ),
            response_stage=ResponseRagStage(
                before_response_modules=[
                    RulesetsBeforeResponseRagModule(rulesets=self.rulesets),
                    MetadataBeforeResponseRagModule(),
                ],
                response_module=PromptResponseRagModule(prompt_driver=self.config.prompt_driver),
            ),
        )

    @property
    def default_task_memory(self) -> TaskMemory:
        return TaskMemory(
            artifact_storages={
                TextArtifact: TextArtifactStorage(
                    rag_engine=self.rag_engine,
                    retrieval_rag_module_name="VectorStoreRetrievalRagModule",
                    vector_store_driver=self.config.vector_store_driver,
                    summary_engine=PromptSummaryEngine(prompt_driver=self.config.prompt_driver),
                    csv_extraction_engine=CsvExtractionEngine(prompt_driver=self.config.prompt_driver),
                    json_extraction_engine=JsonExtractionEngine(prompt_driver=self.config.prompt_driver),
                ),
                BlobArtifact: BlobArtifactStorage(),
            },
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

    def context(self, task: BaseTask) -> dict[str, Any]:
        return {"args": self.execution_args, "structure": self}

    def resolve_relationships(self) -> None:
        task_by_id = {task.id: task for task in self.tasks}

        for task in self.tasks:
            # Ensure parents include this task as a child
            for parent_id in task.parent_ids:
                if parent_id not in task_by_id:
                    raise ValueError(f"Task with id {parent_id} doesn't exist.")
                parent = task_by_id[parent_id]
                if task.id not in parent.child_ids:
                    parent.child_ids.append(task.id)

            # Ensure children include this task as a parent
            for child_id in task.child_ids:
                if child_id not in task_by_id:
                    raise ValueError(f"Task with id {child_id} doesn't exist.")
                child = task_by_id[child_id]
                if task.id not in child.parent_ids:
                    child.parent_ids.append(task.id)

    @observable
    def before_run(self, args: Any) -> None:
        self._execution_args = args

        [task.reset() for task in self.tasks]

        self.publish_event(
            StartStructureRunEvent(
                structure_id=self.id,
                input_task_input=self.input_task.input,
                input_task_output=self.input_task.output,
            ),
        )

        self.resolve_relationships()

    @observable
    def after_run(self) -> None:
        self.publish_event(
            FinishStructureRunEvent(
                structure_id=self.id,
                output_task_input=self.output_task.input,
                output_task_output=self.output_task.output,
            ),
            flush=True,
        )

    @abstractmethod
    def add_task(self, task: BaseTask) -> BaseTask: ...

    @observable
    def run(self, *args) -> Structure:
        self.before_run(args)

        result = self.try_run(*args)

        self.after_run()

        return result

    @abstractmethod
    def try_run(self, *args) -> Structure: ...
