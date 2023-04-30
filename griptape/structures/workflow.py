from __future__ import annotations
import concurrent.futures as futures
import json
from graphlib import TopologicalSorter
from attr import define, field
from griptape.artifacts import ErrorArtifact
from griptape.tasks import BaseTask
from griptape.structures import Structure
from griptape.utils import J2


@define
class Workflow(Structure):
    executor: futures.Executor = field(default=futures.ThreadPoolExecutor(), kw_only=True)

    def add_task(self, task: BaseTask) -> BaseTask:
        task.structure = self

        self.tasks.append(task)

        return task

    def prompt_stack(self, task: BaseTask) -> list[str]:
        stack = Structure.prompt_stack(self, task)

        stack.append(
            J2("prompts/workflow.j2").render(
                task=task
            )
        )

        return stack

    def run(self, *args) -> list[BaseTask]:
        self._execution_args = args
        ordered_tasks = self.order_tasks()
        exit_loop = False

        while not self.is_finished() and not exit_loop:
            futures_list = {}

            for task in ordered_tasks:
                if task.can_execute():
                    future = self.executor.submit(task.execute)
                    futures_list[future] = task

            # Wait for all tasks to complete
            for future in futures.as_completed(futures_list):
                if isinstance(future.result(), ErrorArtifact):
                    exit_loop = True

                    break

        self._execution_args = ()

        return self.output_tasks()

    def context(self, task: BaseTask) -> dict[str, any]:
        context = super().context(task)

        context.update(
            {
                "inputs": {parent.id: parent.output.value if parent.output else "" for parent in task.parents},
                "parents": {parent.id: parent for parent in task.parents},
                "children": {child.id: child for child in task.children}
            }
        )

        return context

    def output_tasks(self) -> list[BaseTask]:
        return [task for task in self.tasks if not task.children]

    def to_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}

        for key_task in self.tasks:
            graph[key_task.id] = set()

            for value_task in self.tasks:
                if key_task.id in value_task.child_ids:
                    graph[key_task.id].add(value_task.id)

        return graph

    def order_tasks(self) -> list[BaseTask]:
        return [self.find_task(task_id) for task_id in TopologicalSorter(self.to_graph()).static_order()]

    def to_dict(self) -> dict:
        from griptape.schemas import WorkflowSchema

        return WorkflowSchema().dump(self)

    @classmethod
    def from_dict(cls, workflow_dict: dict) -> Workflow:
        from griptape.schemas import WorkflowSchema

        return WorkflowSchema().load(workflow_dict)

    @classmethod
    def from_json(cls, workflow_json: str) -> Workflow:
        return Workflow.from_dict(json.loads(workflow_json))
