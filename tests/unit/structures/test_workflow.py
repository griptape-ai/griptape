import json
from tests.mocks.mock_driver import MockDriver
from warpspeed.rules import Rule
from warpspeed.steps import PromptStep, Step
from warpspeed.structures import Workflow


class TestWorkflow:
    def test_constructor(self):
        rule = Rule("test")
        driver = MockDriver()
        workflow = Workflow(prompt_driver=driver, rules=[rule])

        assert workflow.prompt_driver is driver
        assert len(workflow.steps) == 0
        assert workflow.rules[0].value is "test"

    def test_add_step(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")

        workflow = Workflow(
            prompt_driver=MockDriver()
        )

        workflow.add_step(first_step)
        workflow.add_step(second_step)

        assert len(workflow.steps) == 2
        assert first_step in workflow.steps
        assert second_step in workflow.steps
        assert first_step.structure == workflow
        assert second_step.structure == workflow
        assert len(first_step.parents) == 0
        assert len(first_step.children) == 0
        assert len(second_step.parents) == 0
        assert len(second_step.children) == 0

    def test_add_steps(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")

        workflow = Workflow(
            prompt_driver=MockDriver()
        )

        workflow.add_steps(first_step, second_step)

        assert len(workflow.steps) == 2
        assert first_step in workflow.steps
        assert second_step in workflow.steps
        assert first_step.structure == workflow
        assert second_step.structure == workflow
        assert len(first_step.parents) == 0
        assert len(first_step.children) == 0
        assert len(second_step.parents) == 0
        assert len(second_step.children) == 0

    def test_run(self):
        step1 = PromptStep("test")
        step2 = PromptStep("test")
        workflow = Workflow(prompt_driver=MockDriver())
        workflow.add_steps(step1, step2)

        assert step1.state == Step.State.PENDING
        assert step2.state == Step.State.PENDING

        workflow.run()

        assert step1.state == Step.State.FINISHED
        assert step2.state == Step.State.FINISHED

    def test_run_with_args(self):
        step = PromptStep("{{ args[0] }}-{{ args[1] }}")
        workflow = Workflow(prompt_driver=MockDriver())
        workflow.add_steps(step)

        workflow._execution_args = ("test1", "test2")

        assert step.render_prompt() == "test1-test2"

        workflow.run()

        assert step.render_prompt() == "-"

    def test_run_topology_1(self):
        step1 = PromptStep("prompt1")
        step2 = PromptStep("prompt2")
        step3 = PromptStep("prompt3")
        workflow = Workflow(prompt_driver=MockDriver())

        # step1 splits into step2 and step3
        workflow.add_step(step1)
        step1.add_child(step2)
        step3.add_parent(step1)

        workflow.run()

        assert step1.state == Step.State.FINISHED
        assert step2.state == Step.State.FINISHED
        assert step3.state == Step.State.FINISHED

    def test_run_topology_2(self):
        step1 = PromptStep("test1")
        step2 = PromptStep("test2")
        step3 = PromptStep("test3")
        workflow = Workflow(prompt_driver=MockDriver())

        # step1 and step2 converge into step3
        workflow.add_steps(step1, step2)
        step1.add_child(step3)
        step3.add_parent(step2)

        workflow.run()

        assert step1.state == Step.State.FINISHED
        assert step2.state == Step.State.FINISHED
        assert step3.state == Step.State.FINISHED

    def test_output_steps(self):
        step1 = PromptStep("prompt1")
        step2 = PromptStep("prompt2")
        step3 = PromptStep("prompt3")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(step1)
        step1.add_child(step2)
        step3.add_parent(step1)

        assert len(workflow.output_steps()) == 2
        assert step2 in workflow.output_steps()
        assert step3 in workflow.output_steps()

    def test_to_graph(self):
        step1 = PromptStep("prompt1", id="step1")
        step2 = PromptStep("prompt2", id="step2")
        step3 = PromptStep("prompt3", id="step3")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(step1)
        step1.add_child(step2)
        step3.add_parent(step1)

        graph = workflow.to_graph()

        assert "step1" in graph["step2"]
        assert "step1" in graph["step3"]

    def test_order_steps(self):
        step1 = PromptStep("prompt1")
        step2 = PromptStep("prompt2")
        step3 = PromptStep("prompt3")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(step1)
        step1.add_child(step2)
        step3.add_parent(step1)

        ordered_steps = workflow.order_steps()

        assert ordered_steps[0] == step1
        assert ordered_steps[1] == step2 or ordered_steps[1] == step3
        assert ordered_steps[2] == step2 or ordered_steps[2] == step3

    def test_to_json(self):
        workflow = Workflow()

        workflow.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        assert len(json.loads(workflow.to_json())["steps"]) == 2

    def test_to_dict(self):
        workflow = Workflow()

        workflow.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        assert len(workflow.to_dict()["steps"]) == 2

    def test_from_json(self):
        workflow = Workflow()

        workflow.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        workflow_json = workflow.to_json()

        assert len(Workflow.from_json(workflow_json).steps) == 2

    def test_from_dict(self):
        workflow = Workflow()

        workflow.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        workflow_json = workflow.to_dict()

        assert len(Workflow.from_dict(workflow_json).steps) == 2

    def test_context(self):
        parent = PromptStep("parent")
        step = PromptStep("test")
        child = PromptStep("child")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(parent)

        parent.add_child(step)
        step.add_child(child)

        context = workflow.context(step)

        assert context["inputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(step)

        assert context["inputs"] == {parent.id: parent.output.value}
        assert context["structure"] == workflow
        assert context["parents"] == {parent.id: parent}
        assert context["children"] == {child.id: child}
