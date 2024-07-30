from __future__ import annotations

import base64
import hashlib
from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from griptape.structures import Structure
    from griptape.tasks import BaseTask


@define
class StructureVisualizer:
    """Utility class to visualize a Structure structure."""

    structure: Structure = field()
    header: str = field(default="graph TD;", kw_only=True)

    def to_url(self) -> str:
        """Generates a url that renders the Workflow structure as a Mermaid flowchart.

        Reference: https://mermaid.js.org/ecosystem/tutorials#jupyter-integration-with-mermaid-js.

        Returns:
            str: URL to the rendered image
        """
        self.structure.resolve_relationships()

        tasks = "\n\t" + "\n\t".join([self.__render_task(task) for task in self.structure.tasks])
        graph = f"{self.header}{tasks}"

        graph_bytes = graph.encode("utf-8")
        base64_string = base64.b64encode(graph_bytes).decode("utf-8")

        url = f"https://mermaid.ink/svg/{base64_string}"
        return url

    def __render_task(self, task: BaseTask) -> str:
        if task.children:
            children = " & ".join([f"{self.__get_id(child.id)}({child.id})" for child in task.children])
            return f"{self.__get_id(task.id)}({task.id})--> {children};"
        else:
            return f"{self.__get_id(task.id)}({task.id});"

    def __get_id(self, string: str) -> str:
        return hashlib.md5(string.encode()).hexdigest()[:8]
