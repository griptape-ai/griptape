from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Callable

from attrs import define, field

if TYPE_CHECKING:
    from griptape.structures import Structure
    from griptape.tasks import BaseTask


@define
class StructureVisualizer:
    """Utility class to visualize a Structure structure."""

    structure: Structure = field()
    header: str = field(default="graph TD;", kw_only=True)
    build_node_id: Callable[[BaseTask], str] = field(default=lambda task: task.id.title(), kw_only=True)

    def to_url(self) -> str:
        """Generates a url that renders the Workflow structure as a Mermaid flowchart.

        Reference: https://mermaid.js.org/ecosystem/tutorials#jupyter-integration-with-mermaid-js.

        Returns:
            str: URL to the rendered image
        """
        self.structure.resolve_relationships()

        tasks = self.__render_tasks(self.structure.tasks)
        graph = f"{self.header}{tasks}"

        graph_bytes = graph.encode("utf-8")
        base64_string = base64.b64encode(graph_bytes).decode("utf-8")

        return f"https://mermaid.ink/svg/{base64_string}"

    def __render_tasks(self, tasks: list[BaseTask]) -> str:
        return "\n\t" + "\n\t".join([self.__render_task(task) for task in tasks])

    def __render_task(self, task: BaseTask) -> str:
        from griptape.drivers import LocalStructureRunDriver
        from griptape.tasks import StructureRunTask

        parts = []
        if task.children:
            children = " & ".join([f"{self.build_node_id(child)}" for child in task.children])
            parts.append(f"{self.build_node_id(task)}--> {children};")
        else:
            parts.append(f"{self.build_node_id(task)};")

        if isinstance(task, StructureRunTask) and isinstance(task.structure_run_driver, LocalStructureRunDriver):
            sub_structure = task.structure_run_driver.create_structure()
            sub_tasks = self.__render_tasks(sub_structure.tasks)
            parts.append(f"subgraph {self.build_node_id(task)}{sub_tasks}\n\tend")

        return "\n\t".join(parts)
