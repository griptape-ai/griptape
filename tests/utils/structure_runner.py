import os
import re
from json import loads
from textwrap import dedent

from griptape.drivers import (
    AmazonBedrockPromptDriver,
    AnthropicPromptDriver,
    BedrockClaudePromptModelDriver,
    BedrockJurassicPromptModelDriver,
    BedrockTitanPromptModelDriver,
    CoherePromptDriver,
    OpenAiChatPromptDriver,
    OpenAiCompletionPromptDriver,
    AzureOpenAiCompletionPromptDriver,
    AzureOpenAiChatPromptDriver,
    AmazonSageMakerPromptDriver,
    SageMakerLlamaPromptModelDriver,
    SageMakerFalconPromptModelDriver,
)
from griptape.rules import Rule, Ruleset

OUTPUT_RULESET = Ruleset(
    name="Output Format",
    rules=[
        Rule(
            value=dedent(
                """Write your output in json with the following schema: 
                {
                  "$schema": "http://json-schema.org/draft-04/schema#",
                  "type": "object",
                  "properties": {
                    "task_output": {
                      "type": "string"
                    },
                    "task_result": {
                      "type": "string"
                      "oneOf": [
                        "success",
                        "failure"
                      ]
                    }
                  },
                  "required": [
                    "task_output",
                    "task_result"
                  ]
                }
                If there is an error or the answer is incorrect, task_result should be "failure".
                """
            )
        )
    ],
)


PROMPT_DRIVERS = {
    "OPENAI_CHAT_35": OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"]),
    "OPENAI_CHAT_4": OpenAiChatPromptDriver(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"]),
    "OPENAI_COMPLETION_DAVINCI": OpenAiCompletionPromptDriver(
        api_key=os.environ["OPENAI_API_KEY"], model="text-davinci-003"
    ),
    "AZURE_CHAT_35": AzureOpenAiChatPromptDriver(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model="gpt-35-turbo-16k",
        deployment_id=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_ID"],
        api_base=os.environ["AZURE_OPENAI_API_BASE"],
    ),
    "AZURE_CHAT_4": AzureOpenAiChatPromptDriver(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model="gpt-4-32k",
        deployment_id=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_ID"],
        api_base=os.environ["AZURE_OPENAI_API_BASE"],
    ),
    "AZURE_COMPLETION_DAVINCI": AzureOpenAiCompletionPromptDriver(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model="text-davinci-003",
        deployment_id=os.environ["AZURE_OPENAI_COMPLETION_DEPLOYMENT_ID"],
        api_base=os.environ["AZURE_OPENAI_API_BASE"],
    ),
    "ANTHROPIC_CLAUDE_2": AnthropicPromptDriver(model="claude-2", api_key=os.environ["ANTHROPIC_API_KEY"]),
    "COHERE_COMMAND": CoherePromptDriver(
        api_key=os.environ["COHERE_API_KEY"],
    ),
    "BEDROCK_TITAN": AmazonBedrockPromptDriver(
        model="amazon.titan-tg1-large",
        prompt_model_driver=BedrockTitanPromptModelDriver(),
    ),
    "BEDROCK_CLAUDE_2": AmazonBedrockPromptDriver(
        model="anthropic.claude-v2",
        prompt_model_driver=BedrockClaudePromptModelDriver(),
    ),
    "BEDROCK_J2": AmazonBedrockPromptDriver(
        model="ai21.j2-ultra", prompt_model_driver=BedrockJurassicPromptModelDriver()
    ),
    "SAGEMAKER_LLAMA_7B": AmazonSageMakerPromptDriver(
        model=os.environ["SAGEMAKER_LLAMA_ENDPOINT_NAME"],
        prompt_model_driver=SageMakerLlamaPromptModelDriver(max_tokens=4096),
    ),
    "SAGEMAKER_FALCON_7b": AmazonSageMakerPromptDriver(
        model=os.environ["SAGEMAKER_FALCON_ENDPOINT_NAME"],
        prompt_model_driver=SageMakerFalconPromptModelDriver(),
    ),
}

TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS = [
    PROMPT_DRIVERS["OPENAI_CHAT_4"],
    PROMPT_DRIVERS["OPENAI_CHAT_35"],
    PROMPT_DRIVERS["OPENAI_COMPLETION_DAVINCI"],
    PROMPT_DRIVERS["AZURE_CHAT_35"],
    PROMPT_DRIVERS["AZURE_COMPLETION_DAVINCI"],
    PROMPT_DRIVERS["ANTHROPIC_CLAUDE_2"],
    PROMPT_DRIVERS["BEDROCK_CLAUDE_2"],
    PROMPT_DRIVERS["BEDROCK_J2"],
]

TOOL_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()

PROMPT_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()

SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()


def prompt_driver_id_fn(prompt_driver) -> str:
    return f"{prompt_driver.__class__.__name__}-{prompt_driver.model}"


def run_structure(structure, prompt) -> dict:
    result = structure.run(prompt)
    output_text = result.output.to_text()
    json_matches = re.findall(r"[^{]*({.*})", output_text, re.DOTALL)
    if json_matches:
        return loads(json_matches[0], strict=False)
    return {"task_output": output_text, "task_result": "maybe"}
