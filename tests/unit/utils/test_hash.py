from griptape import utils


class TestHash:
    def test_str_to_hash(self):
        assert (
            utils.str_to_hash("foo")
            == "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
        )
        assert (
            utils.str_to_hash("foo", "md5")
            == "acbd18db4cc2f85cedef654fccc4a4d8"
        )
