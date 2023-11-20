from typing import Callable, Optional, Dict, Any
from attr import define, field, Factory
from griptape.utils import PromptStack
from griptape.artifacts import TextArtifact
from .base_processors import BasePromptStackProcessor
import boto3
from botocore.client import BaseClient


@define
class AmazonComprehendPiiProcessor(BasePromptStackProcessor):
    comprehend_client: BaseClient = field(
        default=Factory(lambda: boto3.client("comprehend", region_name="us-west-2")), kw_only=True
    )
    custom_filter_func: Optional[Callable[[str], str]] = field(default=None, kw_only=True)
    pii_replacements: Dict[str, str] = field(default=Factory(dict), kw_only=True)

    def before_run(self, prompt_stack: PromptStack) -> PromptStack:
        for input_item in prompt_stack.inputs:
            input_item.content = self.filter_pii(input_item.content)

        return prompt_stack

    def after_run(self, result: TextArtifact) -> TextArtifact:
        result_text = result.value  # Extract the text from the TextArtifact object

        for pii_replace_text, original_pii in self.pii_replacements.items():
            result_text = result_text.replace(pii_replace_text, original_pii)

        # Replace the text in the TextArtifact object
        result.value = result_text

        return result

    def filter_pii(self, text: str) -> str:
        if self.custom_filter_func:
            return self.custom_filter_func(text)

        text = text.encode("utf-8").decode("utf-8")
        response = self.comprehend_client.detect_pii_entities(Text=text, LanguageCode="en")

        pii_entities = response.get("Entities", [])
        text_copy = text

        pii_entities.sort(key=lambda e: e["BeginOffset"], reverse=True)

        for i, entity in enumerate(pii_entities):
            entity_start = entity["BeginOffset"]
            entity_end = entity["EndOffset"]
            original_pii = text_copy[entity_start:entity_end]
            pii_replace_text = f"[PII{i}]"
            text_copy = text_copy[:entity_start] + pii_replace_text + text_copy[entity_end:]
            self.pii_replacements[pii_replace_text] = original_pii

        return text_copy if text_copy else "No text to process"
