class TestWorkflows:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/structures/workflows/
    """

    def test_workflows(self):
        from griptape.tasks import PromptTask
        from griptape.structures import Workflow

        def character_task(task_id, character_name) -> PromptTask:
            return PromptTask(
                "Based on the following world description create a character named {{ name }}:\n{{ parent_outputs['world'] }}",
                context={"name": character_name},
                id=task_id,
            )

        world_task = PromptTask(
            "Create a fictional world based on the following key words {{ keywords|join(', ') }}",
            context={"keywords": ["fantasy", "ocean", "tidal lock"]},
            id="world",
        )

        character_task_1 = character_task("scotty", "Scotty")
        character_task_2 = character_task("annie", "Annie")

        story_task = PromptTask(
            "Based on the following description of the world and characters, write a short story:\n{{ parent_outputs['world'] }}\n{{ parent_outputs['scotty'] }}\n{{ parent_outputs['annie'] }}",
            id="story",
        )

        workflow = Workflow()

        workflow.add_task(world_task)

        world_task.add_child(character_task_1)
        world_task.add_child(character_task_2)
        world_task.add_child(story_task)

        character_task_1.add_child(story_task)
        character_task_2.add_child(story_task)

        result = workflow.run()

        for task in result:
            assert task.output is not None
