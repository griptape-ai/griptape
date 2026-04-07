from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.common.prompt_stack.prompt_stack import PromptStack
from griptape.drivers.prompt.perplexity_prompt_driver import PerplexityPromptDriver
from griptape.drivers.web_search import BaseWebSearchDriver
from griptape.utils.decorators import lazy_property


@define
class PerplexityWebSearchDriver(BaseWebSearchDriver):
    model: str = field(default="sonar-pro", kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(kw_only=True, default=None)
    _prompt_driver: Optional[PerplexityPromptDriver] = field(default=None, alias="prompt_driver")

    @lazy_property()
    def prompt_driver(self) -> PerplexityPromptDriver:
        if self.api_key is None:
            raise ValueError("api_key is required")
        return PerplexityPromptDriver(model=self.model, api_key=self.api_key)

    def search(self, query: str, **kwargs) -> ListArtifact:
        message = self.prompt_driver.run(PromptStack.from_artifact(TextArtifact(query)))

        return ListArtifact([message.to_artifact()])
