from griptape.utils import remove_null_values_in_dict_recursively


class TestDictUtils:
    def test_remove_null_values_in_dict_recursively(self):
        dict_with_nones = {
            "foo": None,
            "bar": {"baz": {"foo": [1, 2, 3], "bar": None}},
        }

        dict_without_nones = {"bar": {"baz": {"foo": [1, 2, 3]}}}

        assert (
            remove_null_values_in_dict_recursively(dict_with_nones)
            == dict_without_nones
        )
