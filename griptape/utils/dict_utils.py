from __future__ import annotations

from typing import Optional


def remove_null_values_in_dict_recursively(d: dict) -> dict:
    if isinstance(d, dict):
        return {k: remove_null_values_in_dict_recursively(v) for k, v in d.items() if v is not None}
    else:
        return d


def remove_key_in_dict_recursively(d: dict, key: str) -> dict:
    if isinstance(d, dict):
        return {k: remove_key_in_dict_recursively(v, key) for k, v in d.items() if k != key}
    else:
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
