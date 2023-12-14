import os
from attr import field, define
from schema import Schema, Literal
import logging
import json

from griptape.structures import Structure
from griptape.drivers import (
    AmazonBedrockPromptDriver,
    AnthropicPromptDriver,
    BedrockClaudePromptModelDriver,
    BedrockJurassicPromptModelDriver,
    BedrockTitanPromptModelDriver,
    CoherePromptDriver,
    OpenAiChatPromptDriver,
    OpenAiCompletionPromptDriver,
    AzureOpenAiChatPromptDriver,
    AmazonSageMakerPromptDriver,
    SageMakerLlamaPromptModelDriver,
    SageMakerFalconPromptModelDriver,
)


@define
class StructureTester:
    PROMPT_DRIVERS = {
        "OPENAI_CHAT_35": OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"]),
        "OPENAI_CHAT_4": OpenAiChatPromptDriver(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"]),
        "OPENAI_CHAT_4_1106_PREVIEW": OpenAiChatPromptDriver(
            model="gpt-4-1106-preview", api_key=os.environ["OPENAI_API_KEY"]
        ),
        "OPENAI_COMPLETION_DAVINCI": OpenAiCompletionPromptDriver(
            api_key=os.environ["OPENAI_API_KEY"], model="text-davinci-003"
        ),
        "AZURE_CHAT_35_TURBO": AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            model="gpt-35-turbo",
            azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
        ),
        "AZURE_CHAT_35_TURBO_16k": AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            model="gpt-35-turbo-16k",
            azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_16k_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
        ),
        "AZURE_CHAT_4": AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            model="gpt-4",
            azure_deployment=os.environ["AZURE_OPENAI_4_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
        ),
        "AZURE_CHAT_4_32k": AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            model="gpt-4-32k",
            azure_deployment=os.environ["AZURE_OPENAI_4_32k_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_API_BASE"],
        ),
        "ANTHROPIC_CLAUDE_2": AnthropicPromptDriver(model="claude-2", api_key=os.environ["ANTHROPIC_API_KEY"]),
        "COHERE_COMMAND": CoherePromptDriver(model="command", api_key=os.environ["COHERE_API_KEY"]),
        "BEDROCK_TITAN": AmazonBedrockPromptDriver(
            model="amazon.titan-tg1-large", prompt_model_driver=BedrockTitanPromptModelDriver()
        ),
        "BEDROCK_CLAUDE_2": AmazonBedrockPromptDriver(
            model="anthropic.claude-v2", prompt_model_driver=BedrockClaudePromptModelDriver()
        ),
        "BEDROCK_J2": AmazonBedrockPromptDriver(
            model="ai21.j2-ultra", prompt_model_driver=BedrockJurassicPromptModelDriver()
        ),
        "SAGEMAKER_LLAMA_7B": AmazonSageMakerPromptDriver(
            model=os.environ["SAGEMAKER_LLAMA_ENDPOINT_NAME"],
            prompt_model_driver=SageMakerLlamaPromptModelDriver(max_tokens=4096),
        ),
        "SAGEMAKER_FALCON_7b": AmazonSageMakerPromptDriver(
            model=os.environ["SAGEMAKER_FALCON_ENDPOINT_NAME"], prompt_model_driver=SageMakerFalconPromptModelDriver()
        ),
    }

    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS = [
        PROMPT_DRIVERS["OPENAI_CHAT_4"],
        PROMPT_DRIVERS["AZURE_CHAT_4"],
        PROMPT_DRIVERS["AZURE_CHAT_4_32k"],
        PROMPT_DRIVERS["AZURE_CHAT_4_1106_PREVIEW"],
        PROMPT_DRIVERS["ANTHROPIC_CLAUDE_2"],
    ]

    TOOL_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()

    PROMPT_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()

    SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS = PROMPT_DRIVERS.values()

    structure: Structure = field()

    @classmethod
    def prompt_driver_id_fn(cls, prompt_driver) -> str:
        return f"{prompt_driver.__class__.__name__}-{prompt_driver.model}"

    def llm_assert(self, actual, expected, task_names) -> bool:
        from griptape.structures import Agent
        from griptape.rules import Rule, Ruleset
        from griptape.tasks import PromptTask

        output_schema = Schema(
            {
                Literal("correct", description="Whether the output was correct or not."): bool,
                Literal(
                    "explanation", description="A brief explanation of why you felt the output was correct or not."
                ): str,
            }
        )

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
                            "Your objective is to determine whether an LLM generates an acceptable output for a given prompt and tasks."
                        ),
                        Rule("The output does not need to be perfect, but it should be acceptable"),
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
                    "Tasks: {{ task_names }}\nPrompt: {{ prompt }}.\nOutput: {{ output }}.",
                    context={"prompt": expected, "output": actual, "task_names": ", ".join(task_names)},
                )
            ],
            logger_level=logging.DEBUG,
        )
        agent.logger.debug("Determining correctness of output.")
        result = json.loads(agent.run().output_task.output.to_text())
        correct = result["correct"] is True
        explanation = result["explanation"]

        agent.logger.debug(explanation)

        return correct

    def run(self, prompt) -> str:
        result = self.structure.run(prompt)
        output_text = result.output_task.output.to_text()
        task_names = [task.__class__.__name__ for task in self.structure.tasks]
        assert self.llm_assert(output_text, prompt, task_names)

        return output_text
