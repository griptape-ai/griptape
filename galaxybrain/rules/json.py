import json
from galaxybrain.rules.rule import Rule


def return_valid_json() -> Rule:
    return Rule(
        "only output valid JSON",
        validator=lambda result: __is_valid_json(result.value)
    )


def return_array() -> Rule:
    return Rule(
        "only output a valid JSON array",
        validator=lambda result: __is_json_array(result.value)
    )


def return_object() -> Rule:
    return Rule(
        "only output a valid JSON object",
        validator=lambda result: __is_json_object(result.value)
    )


def put_answer_in_field(value: str) -> Rule:
    return Rule(
        f"only output a valid JSON object with your answer in '{value}'",
        validator=lambda result: __has_key_in_json_object(result.value, value)
    )


def __is_valid_json(json_string: str) -> bool:
    try:
        json.loads(json_string)

        return True
    except json.decoder.JSONDecodeError:
        return False


def __is_json_array(string):
    try:
        json_data = json.loads(string)

        if isinstance(json_data, list):
            return True
        else:
            return False
    except:
        return False


def __is_json_object(string):
    try:
        json_data = json.loads(string)

        if isinstance(json_data, dict):
            return True
        else:
            return False
    except:
        return False


def __has_key_in_json_object(json_string: str, key: str) -> bool:
    try:
        json_data = json.loads(json_string)

        if key in json_data:
            return True
        return False
    except json.decoder.JSONDecodeError:
        return False


def __has_keys_in_json_array(json_string: str, key: str) -> bool:
    try:
        json_data = json.loads(json_string)

        return all([__has_key_in_json_object(json.dumps(json_obj), key) for json_obj in json_data])
    except json.decoder.JSONDecodeError:
        return False
