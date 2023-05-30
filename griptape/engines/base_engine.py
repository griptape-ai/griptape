from abc import ABC
from attr import define, field, Factory
from griptape.drivers import BasePromptDriver, OpenAiPromptDriver


@define
class BaseEngine(ABC):
    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: OpenAiPromptDriver()),
        kw_only=True
    )
