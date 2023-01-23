from galaxybrain.rules.rule import Rule


def be_truthful() -> Rule:
    return Rule(
        "be truthful and say \"I don't know\" if you don't know an answer to the question",
        validator=lambda result: True
    )


def your_name_is(name: str) -> Rule:
    return Rule(
        f"you are a chat bot that responds to name \"{name}\"",
        validator=lambda result: True
    )
