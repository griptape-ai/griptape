from unittest.mock import Mock

from tests.unit.tasks.test_base_task import MockTask


class TestRunnableMixin:
    def test_before_run(self):
        mock_on_before_run = Mock()
        mock_task = MockTask(on_before_run=mock_on_before_run)

        mock_task.run()

        assert mock_on_before_run.called

    def test_after_run(self):
        mock_on_after_run = Mock()
        mock_task = MockTask(on_after_run=mock_on_after_run)

        mock_task.run()

        assert mock_on_after_run.called
