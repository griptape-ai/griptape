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

            assert result[0] == "foo-bar"
            assert result[1] == "baz-bar"

    def foobar(self, foo):
        return f"{foo}-bar"
