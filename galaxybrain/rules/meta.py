from galaxybrain.rules.rule import Rule


def be_truthful() -> Rule:
    return Rule(
        "be truthful and say \"I don't know\" if you don't know an answer to the question",
        validator=lambda result: True
    )


def speculate() -> Rule:
    return Rule(
        "say \"I don't know\" if you don't know the answer to the question but also be creative and speculate what the "
        "possible answer could be",
        validator=lambda result: True
    )


def your_name_is(name: str) -> Rule:
    return Rule(
        f"you are a chat bot that responds to name \"{name}\"",
        validator=lambda result: True
    )
