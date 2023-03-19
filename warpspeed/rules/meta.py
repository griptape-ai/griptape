from warpspeed.rules.rule import Rule


def be_truthful() -> Rule:
    return Rule(
        "be truthful and say \"I don't know\" if you don't have the knowledge to answer a question"
    )


def speculate() -> Rule:
    return Rule(
        "say \"I don't know\" if you don't know the answer to the question but also be creative and speculate what the "
        "possible answer could be"
    )


def your_name_is(name: str) -> Rule:
    return Rule(
        f"respond to name \"{name}\""
    )
