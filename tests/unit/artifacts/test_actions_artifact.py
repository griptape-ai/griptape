import pytest
from griptape.artifacts import ActionsArtifact
from griptape.artifacts.actions_artifact import str_to_dict_converter


class TestActionsArtifact:
    def test___add__(self):
        assert (ActionsArtifact("foo") + ActionsArtifact("bar")).value == "foobar"
        assert (
            len(
                (
                    ActionsArtifact("foo", actions=[ActionsArtifact.Action(tag="foo", name="bar")])
                    + ActionsArtifact("bar", actions=[ActionsArtifact.Action(tag="buzz", name="bazz")])
                ).actions
            )
            == 1
        )

    def test_str_to_dict_converter(self):
        assert str_to_dict_converter({}) == {}
        assert str_to_dict_converter('{"foo": "bar"}') == {"foo": "bar"}

        with pytest.raises(Exception):
            str_to_dict_converter('{"foo":')

    def test_action_input_conversion(self):
        assert ActionsArtifact("foo", actions=[ActionsArtifact.Action(tag="foo", name="bar")]).actions[0].input == {}
        assert ActionsArtifact(
            "foo", actions=[ActionsArtifact.Action(tag="foo", name="bar", input='{"foo": "bar"}')]
        ).actions[0].input == {"foo": "bar"}

        with pytest.raises(Exception):
            assert ActionsArtifact(
                "foo", actions=[ActionsArtifact.Action(tag="foo", name="bar", input="{,]}")]
            ).actions[0].input == {"foo": "bar"}
