from warpspeed.rules.rule import Rule


def return_valid_json() -> Rule:
    return Rule(
        "only output valid JSON"
    )


def return_array() -> Rule:
    return Rule(
        "only output a valid JSON array"
    )


def return_object() -> Rule:
    return Rule(
        "only output a valid JSON object"
    )


def put_answer_in_field(value: str) -> Rule:
    return Rule(
        f"only output a valid JSON object with your answer in '{value}'"
    )
