from concurrent import futures

import pytest

from tests.mocks.mock_futures_executor import MockFuturesExecutor


class TestFuturesExecutorMixin:
    def test_futures_executor(self):
        executor = futures.ThreadPoolExecutor()

        assert MockFuturesExecutor(create_futures_executor=lambda: executor).futures_executor == executor

    def test_deprecated_futures_executor(self):
        mock_executor = MockFuturesExecutor()
        with pytest.warns(DeprecationWarning):
            assert mock_executor.futures_executor
            mock_executor.futures_executor = futures.ThreadPoolExecutor()
