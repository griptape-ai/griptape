from .base_processors import BasePromptStackProcessor
import boto3


class AmazonComprehendPiiProcessor(BasePromptStackProcessor):
    def __init__(self, comprehend_client=None, custom_filter_func=None):
        self.comprehend_client = comprehend_client
        if not self.comprehend_client:
            self.comprehend_client = boto3.client("comprehend")
        self.custom_filter_func = custom_filter_func

    def before_run(self, prompt_stack):
        for input_item in prompt_stack:
            input_item["content"] = self.filter_pii(input_item["content"])
        return prompt_stack

    def filter_pii(self, text):
        if self.custom_filter_func:
            return self.custom_filter_func(text)

        # Default implementation using Amazon Comprehend
        response = self.comprehend_client.detect_pii_entities(
            Text=text, LanguageCode="en"
        )
        pii_entities = response.get("Entities", [])

        # Replace PII entities with mask or redaction
        for entity in pii_entities:
            text = text.replace(entity["Text"], "[PII]")

        return text
