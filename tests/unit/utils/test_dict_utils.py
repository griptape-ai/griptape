import pytest

from griptape.utils import dict_merge, remove_key_in_dict_recursively, remove_null_values_in_dict_recursively


class TestDictUtils:
    def test_remove_null_values_in_dict_recursively(self):
        dict_with_nones = {"foo": None, "bar": {"baz": {"foo": [1, 2, 3], "bar": None}}}

        dict_without_nones = {"bar": {"baz": {"foo": [1, 2, 3]}}}

        assert remove_null_values_in_dict_recursively(dict_with_nones) == dict_without_nones

    def test_remove_key_in_dict_recursively(self):
        dict_with_key = {"foo": 1, "bar": {"baz": {"quxx": [1, 2, 3], "bar": 2}}}

        dict_without_key = {"foo": 1, "bar": {"baz": {"bar": 2}}}

        assert remove_key_in_dict_recursively(dict_with_key, "quxx") == dict_without_key

    def test_dict_merge_merges_dicts(self):
        a = {"a": 1, "b": {"b1": 2, "b2": 3}}
        b = {"a": 1, "b": {"b1": 4}}

        assert dict_merge(a, b)["a"] == 1
        assert dict_merge(a, b)["b"]["b2"] == 3
        assert dict_merge(a, b)["b"]["b1"] == 4

    def test_dict_merge_works_with_optionals(self):
        a = {"a": 1, "b": {"b1": 2, "b2": 3}}
        b = None

        assert dict_merge(a, b)["a"] == 1
        assert dict_merge(a, b)["b"]["b2"] == 3
        assert dict_merge(a, b)["b"]["b1"] == 2

        a = None
        b = {"a": 1, "b": {"b1": 2, "b2": 3}}

        assert dict_merge(a, b)["a"] == 1
        assert dict_merge(a, b)["b"]["b2"] == 3
        assert dict_merge(a, b)["b"]["b1"] == 2

    def test_dict_merge_inserts_new_keys(self):
        a = {"a": 1, "b": {"b1": 2, "b2": 3}}
        b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

        assert dict_merge(a, b)["a"] == 1
        assert dict_merge(a, b)["b"]["b2"] == 3
        assert dict_merge(a, b)["b"]["b1"] == 4
        assert dict_merge(a, b)["b"]["b3"] == 5
        assert dict_merge(a, b)["c"] == 6

    def test_dict_merge_does_not_insert_new_keys(self):
        a = {"a": 1, "b": {"b1": 2, "b2": 3}}
        b = {"a": 1, "b": {"b1": 4, "b3": 5}, "c": 6}

        assert dict_merge(a, b, add_keys=False)["a"] == 1
        assert dict_merge(a, b, add_keys=False)["b"]["b2"] == 3
        assert dict_merge(a, b, add_keys=False)["b"]["b1"] == 4

        with pytest.raises(KeyError):
            assert dict_merge(a, b, add_keys=False)["b"]["b3"] == 5

        with pytest.raises(KeyError):
            assert dict_merge(a, b, add_keys=False)["b"]["b3"] == 6
