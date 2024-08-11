from griptape.engines.rag import RagContext
from tests.mocks.mock_rag_module import MockRagModule


class TestBaseRagModule:
    def test_generate_prompt_stack(self):
        prompt_stack = MockRagModule().generate_prompt_stack("test system", "test query")

        assert len(prompt_stack.messages) == 2
        assert prompt_stack.messages[0].is_system()
        assert prompt_stack.messages[1].is_user()

    def test_generate_prompt_stack_with_empty_system_message(self):
        prompt_stack = MockRagModule().generate_prompt_stack(None, "test query")

        assert len(prompt_stack.messages) == 1
        assert prompt_stack.messages[0].is_user()

    def test_get_context_param(self):
        module = MockRagModule(name="boo")
        context = RagContext(query="test")

        context.module_configs["boo"] = {"foo": "bar"}

        assert module.get_context_param(context, "foo") == "bar"

    def test_set_context_param(self):
        module = MockRagModule(name="boo")
        context = RagContext(query="test")

        module.set_context_param(context, "foo", "bar")

        assert context.module_configs["boo"]["foo"] == "bar"
