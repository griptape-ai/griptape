from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import WebLoader
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.tools import RagTool
from griptape.utils import Chat

namespace = "physics-wiki"

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                vector_store_driver=vector_store_driver, query_params={"namespace": namespace, "top_n": 20}
            )
        ]
    ),
    response_stage=ResponseRagStage(
        response_modules=[PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))]
    ),
)

artifacts = WebLoader().load("https://en.wikipedia.org/wiki/Physics")

vector_store_driver.upsert_text_artifacts({namespace: artifacts})

rag_tool = RagTool(
    description="Contains information about physics. " "Use it to answer any physics-related questions.",
    rag_engine=engine,
)

agent = Agent(
    rulesets=[
        Ruleset(
            name="Physics Tutor",
            rules=[Rule("Always introduce yourself as a physics tutor"), Rule("Be truthful. Only discuss physics.")],
        )
    ],
    tools=[rag_tool],
)

Chat(agent).start()
