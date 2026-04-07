from concurrent import futures

from griptape import utils


class TestFutures:
    def test_execute_futures_dict(self):
        with futures.ThreadPoolExecutor() as executor:
            result = utils.execute_futures_dict(
                {"foo": executor.submit(self.foobar, "foo"), "baz": executor.submit(self.foobar, "baz")}
            )

            assert result["foo"] == "foo-bar"
            assert result["baz"] == "baz-bar"

    def test_execute_futures_list(self):
        with futures.ThreadPoolExecutor() as executor:
            result = utils.execute_futures_list(
                [executor.submit(self.foobar, "foo"), executor.submit(self.foobar, "baz")]
            )

            assert set(result) == {"foo-bar", "baz-bar"}

    def test_execute_futures_list_dict(self):
        with futures.ThreadPoolExecutor() as executor:
            result = utils.execute_futures_list_dict(
                {
                    "test1": [executor.submit(self.foobar, f"foo-{i}") for i in range(1000)],
                    "test2": [executor.submit(self.foobar, f"foo-{i}") for i in range(1000)],
                    "test3": [executor.submit(self.foobar, f"foo-{i}") for i in range(1000)],
                }
            )

            assert len(result["test1"]) == 1000
            assert len(result["test2"]) == 1000
            assert len(result["test3"]) == 1000

    def foobar(self, foo):
        return f"{foo}-bar"
