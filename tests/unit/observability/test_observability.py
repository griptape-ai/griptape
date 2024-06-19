from unittest.mock import MagicMock, Mock
import pytest

from griptape.drivers.observability.no_op_observability_driver import NoOpObservabilityDriver
import griptape.observability.observability as observability
from griptape.observability.observability import Observability


class TestObservability:
    @pytest.fixture
    def mock_observability_driver(self):
        return MagicMock()

    def test_init(self, mock_observability_driver):
        assert observability._global_observability_driver is None

        Observability(observability_driver=mock_observability_driver)

        assert observability._global_observability_driver is None

    def test_context_manager(self, mock_observability_driver):
        assert observability._global_observability_driver is None

        with Observability(observability_driver=mock_observability_driver):
            assert observability._global_observability_driver is mock_observability_driver
            mock_observability_driver.__enter__.assert_called_once_with()

        mock_observability_driver.__exit__.assert_called_once_with(None, None, None)

        assert observability._global_observability_driver is None

    def test_context_manager_exception(self, mock_observability_driver):
        assert observability._global_observability_driver is None

        with pytest.raises(Exception, match="Boom") as e:
            with Observability(observability_driver=mock_observability_driver):
                assert observability._global_observability_driver is mock_observability_driver
                mock_observability_driver.__enter__.assert_called_once_with()
                raise Exception("Boom")

        mock_observability_driver.__exit__.assert_called_once_with(*e._excinfo)
        assert observability._global_observability_driver is None
