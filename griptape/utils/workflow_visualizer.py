from __future__ import annotations
import base64

from attrs import define, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.tasks import BaseTask
    from griptape.structures import Structure


@define
class WorkflowVisualizer:
    """Utility class to visualize a Workflow structure"""

    structure: Structure = field()

    def render(self) -> str:
        """Renders the Workflow structure as a Mermaid flowchart
        Reference: https://mermaid.js.org/ecosystem/tutorials#jupyter-integration-with-mermaid-js

        Returns:
            str: URL to the rendered image
        """
        self.structure.resolve_relationships()

        tasks = "\n\t" + "\n\t".join([self.__render_task(task) for task in self.structure.tasks if task.children])
        graph = f"graph LR;{tasks}"

        graph_bytes = graph.encode("utf-8")
        base64_string = base64.b64encode(graph_bytes).decode("utf-8")

        return f"https://mermaid.ink/img/{base64_string}"

    def __render_task(self, task: BaseTask) -> str:
        return f'{task.id}--> {" & ".join([child.id for child in task.children])};'
