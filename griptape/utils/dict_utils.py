from __future__ import annotations

from typing import Any, Callable, Optional


def remove_null_values_in_dict_recursively(d: dict) -> dict:
    if isinstance(d, dict):
        return {k: remove_null_values_in_dict_recursively(v) for k, v in d.items() if v is not None}
    return d


def remove_key_in_dict_recursively(d: dict, key: str, preserve_under_key: Optional[str] = None) -> dict:
    """Remove a key in a dictionary recursively.

    Args:
        d: The dictionary to remove the key from.
        key: The key to remove.
        preserve_under_key: An optional key to preserve the keys directly under it.
    """
    if isinstance(d, dict):
        # when we encounter the preserved container,
        # we keep its keys intact, but still recurse into
        # their values to remove nested occurrences of [key].
        if preserve_under_key is not None and preserve_under_key in d and isinstance(d[preserve_under_key], dict):
            preserved_section = {
                inner_k: remove_key_in_dict_recursively(inner_v, key, preserve_under_key)
                for inner_k, inner_v in d[preserve_under_key].items()
            }

            # filter out [key] and recurse in other keys normally.
            result = {k: remove_key_in_dict_recursively(v, key, preserve_under_key) for k, v in d.items() if k != key}
            result[preserve_under_key] = preserved_section
            return result

        return {k: remove_key_in_dict_recursively(v, key, preserve_under_key) for k, v in d.items() if k != key}
    return d


def add_key_in_dict_recursively(
    d: Any, key: str, value: Any, criteria: Optional[Callable[[dict], bool]] = None
) -> dict:
    """Add a key in a dictionary recursively.

    Args:
        d: The dictionary to add the key to.
        key: The key to add.
        value: The value to add.
        criteria: An optional function to determine if the key should be added.
    """
    if isinstance(d, dict):
        if criteria is None or criteria(d):
            d[key] = value
        return {k: add_key_in_dict_recursively(v, key, value, criteria) for k, v in d.items()}
    return d


def dict_merge(dct: Optional[dict], merge_dct: Optional[dict], *, add_keys: bool = True) -> dict:
    """Recursive dict merge.

    Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct: onto which the merge is executed
        merge_dct: dct merged into dct
        add_keys: whether to add new keys

    Returns:
        dict: updated dict
    """
    dct = {} if dct is None else dct
    merge_dct = {} if merge_dct is None else merge_dct

    dct = dct.copy()

    if not add_keys:
        merge_dct = {k: merge_dct[k] for k in set(dct).intersection(set(merge_dct))}

    for key in merge_dct:
        if key in dct and isinstance(dct[key], dict):
            dct[key] = dict_merge(dct[key], merge_dct[key], add_keys=add_keys)
        else:
            dct[key] = merge_dct[key]

    return dct
