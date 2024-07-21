from griptape.common.prompt_stack.contents.action_call_delta_message_content import ActionCallDeltaMessageContent


class TestActionCallDeltaMessageContent:
    def test__str__(self):
        content = ActionCallDeltaMessageContent()
        assert str(content) == ""

        content.name = "TestName"
        assert str(content) == "TestName"

        content.path = "test_path"
        assert str(content) == "TestName.test_path"

        content.tag = "test_tag"
        assert str(content) == "TestName.test_path (test_tag)"

        content.partial_input = "partial_input"
        assert str(content) == "TestName.test_path (test_tag) partial_input"

    def test_missing_header__str__(self):
        assert str(ActionCallDeltaMessageContent(partial_input="partial_input")) == "partial_input"

    def test_missing_input__str__(self):
        assert str(ActionCallDeltaMessageContent(tag="tag", name="name", path="path")) == "name.path (tag)"
