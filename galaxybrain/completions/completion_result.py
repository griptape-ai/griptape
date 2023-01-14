from attrs import define


@define
class CompletionResult():
    value: str
    meta: any