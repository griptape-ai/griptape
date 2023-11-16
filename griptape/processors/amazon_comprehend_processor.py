from typing import Callable, Optional, List, Dict, Any, Union
from attr import define, field, Factory
from griptape.utils import PromptStack
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
        print(f"Before processing: {prompt_stack.inputs}")

        for input_item in prompt_stack.inputs:
            input_item.content = self.filter_pii(input_item.content)

        print(f"After processing: {prompt_stack.inputs}")

        return prompt_stack

    def after_run(self, result: Any) -> Any:
        # Replace the PII back to its original form
        for original_pii, replacement in self.pii_replacements.items():
            result = result.replace(replacement, original_pii)

        return result

    def filter_pii(self, text: str) -> str:
        print("filter_pii method called")

        if self.custom_filter_func:
            return self.custom_filter_func(text)

        response = self.comprehend_client.detect_pii_entities(Text=text, LanguageCode="en")

        pii_entities = response.get("Entities", [])
        text_copy = text

        print(f"pii_entities: {pii_entities}")  # Check if pii_entities list is empty

        # Sort entities by their start position in descending order
        pii_entities.sort(key=lambda e: e["BeginOffset"], reverse=True)

        for entity in pii_entities:
            entity_start = entity["BeginOffset"]
            entity_end = entity["EndOffset"]
            original_pii = text_copy[entity_start:entity_end]
            text_copy = text_copy[:entity_start] + self.pii_replace_text + text_copy[entity_end:]

            # Store the original PII and its replacement
            self.pii_replacements[original_pii] = self.pii_replace_text

            # Print the entity_start, entity_end, and text_copy variables
            print(f"Entity start: {entity_start}, Entity end: {entity_end}, Text copy: {text_copy}")

        print(f"pii_replace_text: {self.pii_replace_text}")  # Check if pii_replace_text is correct

        return text_copy

    @property
    def pii_replace_text(self) -> str:
        return "REDACTED"
