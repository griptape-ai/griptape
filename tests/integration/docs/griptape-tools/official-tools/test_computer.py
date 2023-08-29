class TestCalculator:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/computer/
    """

    def test_computer_tool(self):
        import os
        from griptape.tools import Computer

        Computer(
            local_workdir=os.path.abspath(os.path.join(os.getcwd(), "workdir")),
            env_vars={
                "ENV_VAR_1": "foo",
                "ENV_VAR_2": "bar",
            }
        )
