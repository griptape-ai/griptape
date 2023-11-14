from typing import Callable, Optional, List, Dict, Any
from attr import define, field, Factory
from .base_processors import BasePiiProcessor
import boto3


@define
class AmazonComprehendPiiProcessor(BasePiiProcessor):
    comprehend_client: boto3.client = field(
        default=Factory(lambda: boto3.client("comprehend")), kw_only=True
    )
    custom_filter_func: Optional[Callable[[str], str]] = field(
        default=None, kw_only=True
    )

    def before_run(
        self, prompt_stack: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        for input_item in prompt_stack:
            input_item["content"] = self.filter_pii(input_item["content"])
        return prompt_stack

    def after_run(self, result: Any) -> Any:
        ...

    def filter_pii(self, text: str) -> str:
        if self.custom_filter_func:
            return self.custom_filter_func(text)

        # Default implementation using Amazon Comprehend
        response = self.comprehend_client.detect_pii_entities(
            Text=text, LanguageCode="en"
        )
        pii_entities = response.get("Entities", [])

        # Replace PII entities with mask or redaction
        for entity in pii_entities:
            text = text.replace(entity["Text"], self.pii_replace_text)

        return text
