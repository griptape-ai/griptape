from __future__ import annotations
import concurrent.futures as futures
import json
from graphlib import TopologicalSorter
from attrs import define, field
from warpspeed.artifacts import ErrorOutput
from warpspeed.schemas import WorkflowSchema
from warpspeed.steps import Step
from warpspeed.structures import Structure
from warpspeed.utils import J2


@define
class Workflow(Structure):
    executor: futures.Executor = field(default=futures.ThreadPoolExecutor(), kw_only=True)

    def add_step(self, step: Step) -> Step:
        step.structure = self

        self.steps.append(step)

        return step

    def prompt_stack(self, step: Step) -> list[str]:
        stack = Structure.prompt_stack(self, step)

        stack.append(
            J2("prompts/workflow.j2").render(
                step=step
            )
        )

        return stack

    def run(self, *args) -> list[Step]:
        self._execution_args = args
        ordered_steps = self.order_steps()
        exit_loop = False

        while not self.is_finished() and not exit_loop:
            futures_list = {}

            for step in ordered_steps:
                if step.can_execute():
                    future = self.executor.submit(step.execute)
                    futures_list[future] = step

            # Wait for all tasks to complete
            for future in futures.as_completed(futures_list):
                if isinstance(future.result(), ErrorOutput):
                    exit_loop = True

                    break

        self._execution_args = ()

        return self.output_steps()

    def context(self, step: Step) -> dict[str, any]:
        context = super().context(step)

        context.update(
            {
                "inputs": {parent.id: parent.output.value if parent.output else "" for parent in step.parents},
                "parents": {parent.id: parent for parent in step.parents},
                "children": {child.id: child for child in step.children}
            }
        )

        return context

    def output_steps(self) -> list[Step]:
        return [step for step in self.steps if not step.children]

    def to_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}

        for key_step in self.steps:
            graph[key_step.id] = set()

            for value_step in self.steps:
                if key_step.id in value_step.child_ids:
                    graph[key_step.id].add(value_step.id)

        return graph

    def order_steps(self) -> list[Step]:
        return [self.find_step(step_id) for step_id in TopologicalSorter(self.to_graph()).static_order()]

    def to_dict(self) -> dict:
        return WorkflowSchema().dump(self)

    @classmethod
    def from_dict(cls, workflow_dict: dict) -> Workflow:
        return WorkflowSchema().load(workflow_dict)

    @classmethod
    def from_json(cls, workflow_json: str) -> Workflow:
        return Workflow.from_dict(json.loads(workflow_json))
