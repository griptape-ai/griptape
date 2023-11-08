def remove_null_values_in_dict_recursively(d):
    if isinstance(d, dict):
        return {k: remove_null_values_in_dict_recursively(v) for k, v in d.items() if v is not None}
    else:
        return d
