from __future__ import annotations
import os
from attr import field, define
from schema import Schema, Literal
import logging
import json
from griptape.artifacts.error_artifact import ErrorArtifact

from griptape.structures import Agent
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask
from griptape.structures import Structure
from griptape.drivers import (
    BasePromptDriver,
    AmazonBedrockPromptDriver,
    AnthropicPromptDriver,
    BedrockClaudePromptModelDriver,
    BedrockJurassicPromptModelDriver,
    BedrockTitanPromptModelDriver,
    BedrockLlamaPromptModelDriver,
    CoherePromptDriver,
    OpenAiChatPromptDriver,
    OpenAiCompletionPromptDriver,
    AzureOpenAiChatPromptDriver,
    AmazonSageMakerPromptDriver,
    SageMakerLlamaPromptModelDriver,
    SageMakerFalconPromptModelDriver,
    GooglePromptDriver,
)


def get_enabled_prompt_drivers(prompt_drivers_options) -> list[BasePromptDriver]:
    return [
        prompt_driver_option.prompt_driver
        for prompt_driver_option in prompt_drivers_options
        if prompt_driver_option.enabled
    ]


@define
class StructureTester:
    @define
    class TesterPromptDriverOption:
        prompt_driver: BasePromptDriver = field()
        enabled: bool = field()

    PROMPT_DRIVERS = {
        "OPENAI_CHAT_35": TesterPromptDriverOption(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"]),
            enabled=True,
        ),
        "OPENAI_CHAT_35_TURBO_1106": TesterPromptDriverOption(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo-1106", api_key=os.environ["OPENAI_API_KEY"]),
            enabled=True,
        ),
        "OPENAI_CHAT_35_TURBO_INSTRUCT": TesterPromptDriverOption(
            prompt_driver=OpenAiCompletionPromptDriver(
                model="gpt-3.5-turbo-instruct", api_key=os.environ["OPENAI_API_KEY"]
            ),
            enabled=True,
        ),
        "OPENAI_CHAT_4": TesterPromptDriverOption(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"]), enabled=True
        ),
        "OPENAI_CHAT_4_1106_PREVIEW": TesterPromptDriverOption(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4-1106-preview", api_key=os.environ["OPENAI_API_KEY"]),
            enabled=True,
        ),
        "OPENAI_COMPLETION_DAVINCI": TesterPromptDriverOption(
            prompt_driver=OpenAiCompletionPromptDriver(api_key=os.environ["OPENAI_API_KEY"], model="text-davinci-003"),
            enabled=True,
        ),
        "AZURE_CHAT_35_TURBO": TesterPromptDriverOption(
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model="gpt-35-turbo",
                azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
            ),
            enabled=True,
        ),
        "AZURE_CHAT_35_TURBO_16k": TesterPromptDriverOption(
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model="gpt-35-turbo-16k",
                azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
            ),
            enabled=True,
        ),
        "AZURE_CHAT_4": TesterPromptDriverOption(
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model="gpt-4",
                azure_deployment=os.environ["AZURE_OPENAI_4_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
            ),
            enabled=True,
        ),
        "AZURE_CHAT_4_32k": TesterPromptDriverOption(
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model="gpt-4-32k",
                azure_deployment=os.environ["AZURE_OPENAI_4_32k_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
            ),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_2_INSTANT": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(model="claude-instant-1.2", api_key=os.environ["ANTHROPIC_API_KEY"]),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_2": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(model="claude-2.0", api_key=os.environ["ANTHROPIC_API_KEY"]),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_2.1": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(model="claude-2.1", api_key=os.environ["ANTHROPIC_API_KEY"]),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_3_OPUS": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(
                model="claude-3-opus-20240229", api_key=os.environ["ANTHROPIC_API_KEY"]
            ),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_3_SONNET": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(
                model="claude-3-sonnet-20240229", api_key=os.environ["ANTHROPIC_API_KEY"]
            ),
            enabled=True,
        ),
        "ANTHROPIC_CLAUDE_3_HAIKU": TesterPromptDriverOption(
            prompt_driver=AnthropicPromptDriver(
                model="claude-3-haiku-20240307", api_key=os.environ["ANTHROPIC_API_KEY"]
            ),
            enabled=True,
        ),
        "COHERE_COMMAND": TesterPromptDriverOption(
            prompt_driver=CoherePromptDriver(model="command", api_key=os.environ["COHERE_API_KEY"]), enabled=True
        ),
        "BEDROCK_TITAN": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="amazon.titan-tg1-large", prompt_model_driver=BedrockTitanPromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_CLAUDE_INSTANT": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-instant-v1", prompt_model_driver=BedrockClaudePromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_CLAUDE_2": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-v2", prompt_model_driver=BedrockClaudePromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_CLAUDE_2.1": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-v2:1", prompt_model_driver=BedrockClaudePromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_CLAUDE_3_SONNET": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-3-sonnet-20240229-v1:0", prompt_model_driver=BedrockClaudePromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_CLAUDE_3_HAIKU": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-3-haiku-20240307-v1:0", prompt_model_driver=BedrockClaudePromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_J2": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="ai21.j2-ultra", prompt_model_driver=BedrockJurassicPromptModelDriver()
            ),
            enabled=True,
        ),
        "BEDROCK_LLAMA2_13B": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="meta.llama2-13b-chat-v1", prompt_model_driver=BedrockLlamaPromptModelDriver(), max_attempts=1
            ),
            enabled=True,
        ),
        "BEDROCK_LLAMA2_70B": TesterPromptDriverOption(
            prompt_driver=AmazonBedrockPromptDriver(
                model="meta.llama2-70b-chat-v1", prompt_model_driver=BedrockLlamaPromptModelDriver(), max_attempts=1
            ),
            enabled=True,
        ),
        "SAGEMAKER_LLAMA_7B": TesterPromptDriverOption(
            prompt_driver=AmazonSageMakerPromptDriver(
                model=os.environ["SAGEMAKER_LLAMA_ENDPOINT_NAME"],
                prompt_model_driver=SageMakerLlamaPromptModelDriver(max_tokens=4096),
            ),
            enabled=False,
        ),
        "SAGEMAKER_FALCON_7b": TesterPromptDriverOption(
            prompt_driver=AmazonSageMakerPromptDriver(
                model=os.environ["SAGEMAKER_FALCON_ENDPOINT_NAME"],
                prompt_model_driver=SageMakerFalconPromptModelDriver(),
            ),
            enabled=False,
        ),
        "GOOGLE_GEMINI_PRO": TesterPromptDriverOption(
            prompt_driver=GooglePromptDriver(model="gemini-pro", api_key=os.environ["GOOGLE_API_KEY"]), enabled=True
        ),
    }
    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(
        [
            PROMPT_DRIVERS["OPENAI_CHAT_4"],
            PROMPT_DRIVERS["OPENAI_CHAT_4_1106_PREVIEW"],
            PROMPT_DRIVERS["AZURE_CHAT_4"],
            PROMPT_DRIVERS["AZURE_CHAT_4_32k"],
            PROMPT_DRIVERS["ANTHROPIC_CLAUDE_3_OPUS"],
            PROMPT_DRIVERS["GOOGLE_GEMINI_PRO"],
        ]
    )
    TOOL_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    PROMPT_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    TEXT_SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    TEXT_QUERY_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    JSON_EXTRACTION_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    CSV_EXTRACTION_TASK_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())
    RULE_CAPABLE_PROMPT_DRIVERS = get_enabled_prompt_drivers(PROMPT_DRIVERS.values())

    structure: Structure = field()

    @classmethod
    def prompt_driver_id_fn(cls, prompt_driver) -> str:
        return f"{prompt_driver.__class__.__name__}-{prompt_driver.model}"

    def verify_structure_output(self, structure) -> dict:
        output_schema = Schema(
            {
                Literal("correct", description="Whether the output was correct or not."): bool,
                Literal(
                    "explanation", description="A brief explanation of why you felt the output was correct or not."
                ): str,
            }
        )
        task_names = [task.__class__.__name__ for task in structure.tasks]
        prompt = structure.input_task.input.to_text()
        actual = structure.output_task.output.to_text()
        rules = [rule.value for ruleset in structure.input_task.all_rulesets for rule in ruleset.rules]

        agent = Agent(
            rulesets=[
                Ruleset(
                    name="Formatting",
                    rules=[
                        Rule(
                            f"Output a json object matching this schema: {output_schema.json_schema('Output Schema')}."
                        )
                    ],
                ),
                Ruleset(
                    name="Context",
                    rules=[
                        Rule(
                            "Your objective is to determine whether an LLM generated an acceptable output for a given tasks, prompt, and rules."
                        ),
                        Rule("The output does not need to be perfect, but it should be acceptable"),
                        Rule("Do not make any assumptions about how the output should be formatted."),
                        Rule(
                            "Do not worry about the accuracy of the output, only that it is an appropriate response to the prompt."
                        ),
                    ],
                ),
            ],
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                model="gpt-4",
                azure_deployment=os.environ["AZURE_OPENAI_4_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
                response_format="json_object",
            ),
            tasks=[
                PromptTask(
                    "\nTasks: {{ task_names }}"
                    '\n{% if rules %}Rules: """{{ rules }}"""{% endif %}'
                    '\nPrompt: """{{ prompt }}"""'
                    '\nOutput: """{{ output }}"""',
                    context={
                        "prompt": prompt,
                        "output": actual,
                        "task_names": ", ".join(task_names),
                        "rules": ", ".join(rules),
                    },
                )
            ],
            logger_level=logging.DEBUG,
        )
        agent.logger.debug("Determining correctness of output.")
        result = json.loads(agent.run().output_task.output.to_text())
        explanation = result["explanation"]

        agent.logger.debug(explanation)

        return result

    def run(self, prompt, assert_correctness: bool = True) -> dict:
        result = self.structure.run(prompt)
        if isinstance(result.output_task.output, ErrorArtifact):
            verified_result = {"correct": False, "explanation": f"ErrorArtifact: {result.output_task.output.to_text()}"}
        else:
            verified_result = self.verify_structure_output(self.structure)

        if assert_correctness:
            assert verified_result["correct"]

        return verified_result
