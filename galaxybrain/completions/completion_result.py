from attrs import define


@define
class CompletionResult():
    result: str
    meta: any