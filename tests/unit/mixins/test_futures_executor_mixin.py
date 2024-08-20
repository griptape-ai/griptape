from concurrent import futures

from tests.mocks.mock_futures_executor import MockFuturesExecutor


class TestFuturesExecutorMixin:
    def test_futures_executor(self):
        executor = futures.ThreadPoolExecutor()

        assert MockFuturesExecutor(futures_executor_fn=lambda: executor).futures_executor == executor
