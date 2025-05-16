from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from attrs import define, field
from typing_extensions import ParamSpec, Self

from griptape.artifacts import (
    BaseArtifact,
    BlobArtifact,
    BooleanArtifact,
    GenericArtifact,
    JsonArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.events import EventBus, EventListener, FinishStructureRunEvent
from griptape.utils.decorators import lazy_property

P = ParamSpec("P")
T = TypeVar("T")

if TYPE_CHECKING:
    from types import TracebackType

    from griptape.drivers.assistant.griptape_cloud import GriptapeCloudAssistantDriver
    from griptape.drivers.file_manager.griptape_cloud import GriptapeCloudFileManagerDriver
    from griptape.drivers.prompt.griptape_cloud_prompt_driver import GriptapeCloudPromptDriver
    from griptape.observability.observability import Observability
    from griptape.rules import Ruleset
    from griptape.tools import BaseTool, StructureRunTool, VectorStoreTool


@define()
class GriptapeCloudStructure:
    """Utility for working with Griptape Cloud Structures.

    This class provides helpers for interacting with Griptape Cloud-managed resources, such as tools, rulesets, knowledge bases, and structures.
    It reads configuration from environment variables set by the Griptape Cloud runtime.

    Environment Variables:
        - GT_CLOUD_TOOL_DICT: JSON dict mapping tool IDs to parameter dicts for each tool. Each value is a dict of parameters used to instantiate the tool, e.g. {"tool_id_1": {"off_prompt": false, ...}, ...}
        - GT_CLOUD_RULESET_DICT: JSON dict mapping ruleset IDs to parameter dicts for each ruleset. Each value is a dict of parameters for the ruleset.
        - GT_CLOUD_KB_DICT: JSON dict mapping knowledge base IDs to parameter dicts for each knowledge base. Each value is a dict of parameters for the knowledge base.
        - GT_CLOUD_STRUCTURE_DICT: JSON dict mapping structure IDs to parameter dicts for each structure. Each value is a dict of parameters for the structure.
        - GT_CLOUD_ASSISTANT_ID: The assistant ID to use with GriptapeCloudAssistantDriver.
        - GT_CLOUD_BUCKET_ID: The bucket ID for the Griptape Cloud File Manager Driver.
        - GT_CLOUD_API_KEY: The API key for authenticating with Griptape Cloud.
        - GT_CLOUD_STRUCTURE_RUN_ID: The current structure run ID.
        - GT_CLOUD_BASE_URL: The base URL for Griptape Cloud. Defaults to "https://cloud.griptape.ai".

    Attributes:
        _event_listener: Event Listener to use. Defaults to an EventListener with a GriptapeCloudEventListenerDriver.
        _observability: Observability to use. Defaults to an Observability with a GriptapeCloudObservabilityDriver.
        observe: Whether to enable observability. Enabling requires the `drivers-observability-griptape-cloud` extra.
    """

    _event_listener: Optional[EventListener] = field(default=None, kw_only=True, alias="event_listener")
    _observability: Optional[Observability] = field(default=None, kw_only=True, alias="observability")
    observe: bool = field(default=False, kw_only=True)
    _output: Optional[BaseArtifact] = field(default=None, init=False)

    @lazy_property()
    def event_listener(self) -> EventListener:
        """Lazily initializes and returns the default Griptape Cloud EventListener.

        Returns:
            EventListener: An EventListener instance with GriptapeCloudEventListenerDriver.
        """
        from griptape.drivers.event_listener.griptape_cloud import GriptapeCloudEventListenerDriver

        return EventListener(event_listener_driver=GriptapeCloudEventListenerDriver())

    @lazy_property()
    def observability(self) -> Observability:
        """Lazily initializes and returns the default Griptape Cloud Observability.

        Returns:
            Observability: An Observability instance with GriptapeCloudObservabilityDriver.
        """
        from griptape.drivers.observability.griptape_cloud import GriptapeCloudObservabilityDriver
        from griptape.observability.observability import Observability

        return Observability(observability_driver=GriptapeCloudObservabilityDriver())

    @property
    def cloud_file_manager_driver(self) -> GriptapeCloudFileManagerDriver:
        """Gets the Griptape Cloud File Manager Driver.

        Returns:
            GriptapeCloudFileManagerDriver: The file manager driver instance.
        """
        from griptape.drivers.file_manager.griptape_cloud import GriptapeCloudFileManagerDriver

        return GriptapeCloudFileManagerDriver()

    @property
    def prompt_driver(self) -> GriptapeCloudPromptDriver:
        """Gets the Griptape Cloud Prompt Driver.

        Returns:
            GriptapeCloudPromptDriver: The prompt driver instance.
        """
        from griptape.drivers.prompt.griptape_cloud import GriptapeCloudPromptDriver

        return GriptapeCloudPromptDriver()

    @property
    def output(self) -> Optional[BaseArtifact]:
        """Gets the output artifact.

        Returns:
            Optional[BaseArtifact]: The output artifact, if set.
        """
        return self._output

    @output.setter
    def output(self, value: BaseArtifact | Any) -> None:
        """Sets the output artifact, converting the value to an appropriate artifact type if necessary.

        Args:
            value (BaseArtifact | Any): The value to set as output.
        """
        if isinstance(value, BaseArtifact):
            self._output = value
        elif isinstance(value, list):
            self._output = ListArtifact([self._to_artifact(item) for item in value])
        else:
            self._output = self._to_artifact(value)

    @property
    def args(self) -> list[str]:
        """Returns the list of arguments for the structure run.

        Returns:
            list[str]: List of arguments.
        """
        if len(sys.argv) > 1:
            return sys.argv[1:]
        return []

    @property
    def cloud_api_key(self) -> str:
        """Returns the Griptape Cloud API key from the environment variable.

        Returns:
            str: The API key.

        Raises:
            RuntimeError: If the environment variable is not set.
        """
        api_key = os.environ.get("GT_CLOUD_API_KEY")
        if api_key is not None:
            return api_key

        raise RuntimeError("GT_CLOUD_API_KEY environment variable not set.")

    @property
    def structure_run_id(self) -> str:
        """Returns the current structure run ID from the environment variable.

        Returns:
            str: The structure run ID.
        """
        return os.environ["GT_CLOUD_STRUCTURE_RUN_ID"]

    @property
    def in_managed_environment(self) -> bool:
        """Checks if running in a managed Griptape Cloud environment.

        Returns:
            bool: True if in managed environment, False otherwise.
        """
        return "GT_CLOUD_STRUCTURE_RUN_ID" in os.environ

    @property
    def cloud_tool_ids(self) -> list[str]:
        """Returns the list of cloud tool IDs from the environment variable.

        Returns:
            list[str]: List of tool IDs.
        """
        return list(json.loads(os.environ.get("GT_CLOUD_TOOL_DICT", "{}")).keys())

    @property
    def cloud_tools(self) -> list[BaseTool]:
        """Returns a list of cloud tool instances configured from the environment.

        Returns:
            list[BaseTool]: List of cloud tool instances.
        """
        from griptape.tools import GriptapeCloudToolTool, QueryTool

        any_off_prompt = False
        tools = []
        for tool_id, tool_parameters in json.loads(os.environ.get("GT_CLOUD_TOOL_DICT", "{}")).items():
            any_off_prompt = any_off_prompt or tool_parameters.get("off_prompt", False)
            tools.append(
                GriptapeCloudToolTool(
                    tool_id=tool_id,
                    **tool_parameters,
                )
            )

        if any_off_prompt:
            tools.append(QueryTool())

        return tools

    @property
    def cloud_ruleset_ids(self) -> list[str]:
        """Returns the list of cloud ruleset IDs from the environment variable.

        Returns:
            list[str]: List of ruleset IDs.
        """
        return list(json.loads(os.environ.get("GT_CLOUD_RULESET_DICT", "{}")).keys())

    @property
    def cloud_rulesets(self) -> list[Ruleset]:
        """Returns a list of cloud Ruleset instances configured from the environment.

        Returns:
            list[Ruleset]: List of Ruleset instances.
        """
        from griptape.drivers.ruleset.griptape_cloud import GriptapeCloudRulesetDriver
        from griptape.rules import Ruleset

        return [
            Ruleset(
                ruleset_driver=GriptapeCloudRulesetDriver(
                    ruleset_id=ruleset_id,
                ),
                **ruleset_dict,
            )
            for ruleset_id, ruleset_dict in json.loads(os.environ.get("GT_CLOUD_RULESET_DICT", "{}")).items()
        ]

    @property
    def assistant_driver(self) -> GriptapeCloudAssistantDriver:
        """Returns a GriptapeCloudAssistantDriver instance configured from the environment.

        Returns:
            GriptapeCloudAssistantDriver: The assistant driver instance.
        """
        from griptape.drivers.assistant.griptape_cloud import GriptapeCloudAssistantDriver

        return GriptapeCloudAssistantDriver(
            assistant_id=os.environ["GT_CLOUD_ASSISTANT_ID"],
        )

    @property
    def cloud_knowledge_base_ids(self) -> list[str]:
        """Returns the list of cloud knowledge base IDs from the environment variable.

        Returns:
            list[str]: List of knowledge base IDs.
        """
        return list(json.loads(os.environ.get("GT_CLOUD_KB_DICT", "{}")).keys())

    @property
    def knowledge_base_ids(self) -> list[str]:
        """Returns the list of knowledge base IDs from the environment variable.

        Returns:
            list[str]: List of knowledge base IDs.
        """
        return list(json.loads(os.environ.get("GT_CLOUD_KB_DICT", "{}")).keys())

    @property
    def cloud_knowledge_base_tools(self) -> list[VectorStoreTool]:
        """Returns a list of VectorStoreTool instances for each cloud knowledge base configured from the environment.

        Returns:
            list[VectorStoreTool]: List of VectorStoreTool instances.
        """
        from griptape.drivers.vector.griptape_cloud import GriptapeCloudVectorStoreDriver
        from griptape.tools import VectorStoreTool

        return [
            VectorStoreTool(
                vector_store_driver=GriptapeCloudVectorStoreDriver(
                    knowledge_base_id=knowledge_base_id,
                ),
                **knowledge_base_dict,
            )
            for knowledge_base_id, knowledge_base_dict in json.loads(os.environ.get("GT_CLOUD_KB_DICT", "{}")).items()
        ]

    @property
    def cloud_structure_ids(self) -> list[str]:
        """Returns the list of cloud structure IDs from the environment variable.

        Returns:
            list[str]: List of structure IDs.
        """
        return list(json.loads(os.environ.get("GT_CLOUD_STRUCTURE_DICT", "{}")).keys())

    @property
    def cloud_structure_tools(self) -> list[StructureRunTool]:
        """Returns a list of StructureRunTool instances for each cloud structure configured from the environment.

        Returns:
            list[StructureRunTool]: List of StructureRunTool instances.
        """
        from griptape.drivers.structure_run.griptape_cloud import GriptapeCloudStructureRunDriver
        from griptape.tools import StructureRunTool

        return [
            StructureRunTool(
                structure_run_driver=GriptapeCloudStructureRunDriver(
                    structure_id=structure_id,
                    api_key=self.cloud_api_key,
                ),
                **structure_dict,
            )
            for structure_id, structure_dict in json.loads(os.environ.get("GT_CLOUD_STRUCTURE_DICT", "{}")).items()
        ]

    @property
    def all_cloud_tools(self) -> list[BaseTool]:
        """Returns a list of all cloud tools, including regular, knowledge base, and structure tools.

        Returns:
            list[BaseTool]: List of all cloud tool instances.
        """
        return [
            *self.cloud_tools,
            *self.cloud_knowledge_base_tools,
            *self.cloud_structure_tools,
        ]

    def __enter__(self) -> Self:
        """Enters the context manager, setting up event listeners and observability if in a managed environment.

        Returns:
            Self: The current instance.
        """
        from griptape.configs import Defaults
        from griptape.observability.observability import Observability

        Defaults.drivers_config.prompt_driver = self.prompt_driver

        if self.in_managed_environment:
            EventBus.add_event_listener(self.event_listener)

            if self.observe:
                Observability.set_global_driver(self.observability.observability_driver)
                self.observability.observability_driver.__enter__()

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        """Exits the context manager, cleaning up event listeners and observability if in a managed environment.

        Args:
            exc_type (Optional[type[BaseException]]): Exception type, if any.
            exc_value (Optional[BaseException]): Exception value, if any.
            exc_traceback (Optional[TracebackType]): Exception traceback, if any.
        """
        from griptape.observability.observability import Observability

        if self.in_managed_environment:
            if self.output is not None:
                EventBus.publish_event(FinishStructureRunEvent(output_task_output=self.output), flush=True)
            EventBus.remove_event_listener(self.event_listener)

            if self.observe:
                Observability.set_global_driver(None)
                self.observability.observability_driver.__exit__(exc_type, exc_value, exc_traceback)

    def _to_artifact(self, value: Any) -> BaseArtifact:
        """Converts a value to the appropriate BaseArtifact subclass.

        Args:
            value (Any): The value to convert.

        Returns:
            BaseArtifact: The corresponding artifact.
        """
        if isinstance(value, str):
            return TextArtifact(value)
        if isinstance(value, bool):
            return BooleanArtifact(value)
        if isinstance(value, dict):
            return JsonArtifact(value)
        if isinstance(value, bytes):
            return BlobArtifact(value)
        return GenericArtifact(value)
