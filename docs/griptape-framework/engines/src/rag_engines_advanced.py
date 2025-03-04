from rich.pretty import pprint

from griptape.chunkers import TextChunker
from griptape.common.reference import Reference
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.rerank.local import LocalRerankDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.engines.rag import RagContext, RagEngine
from griptape.engines.rag.modules import (
    FootnotePromptResponseRagModule,
    PromptResponseRagModule,
    TextChunksRerankRagModule,
    TextChunksResponseRagModule,
    TextLoaderRetrievalRagModule,
    TranslateQueryRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import (
    QueryRagStage,
    ResponseRagStage,
    RetrievalRagStage,
)
from griptape.loaders import TextLoader, WebLoader
from griptape.rules import Rule, Ruleset

prompt_driver = OpenAiChatPromptDriver(model="gpt-4o")
vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())
rerank_driver = LocalRerankDriver()
web_loader = WebLoader()
text_chunker = TextChunker(max_tokens=250)

# Load some data from a couple sources.
sites = [
    {
        "title": "Griptape Site",
        "url": "https://www.griptape.ai",
    },
    {"title": "Griptape GitHub", "url": "https://github.com/griptape-ai/griptape"},
]
site_artifacts = list(web_loader.load_collection([site["url"] for site in sites]).values())

# Set a reference on each artifact so that the FootnotePromptResponseRagModule can generate footnotes.
for site_arifact, site in zip(site_artifacts, sites):
    site_arifact.reference = Reference(title=site["title"], url=site["url"])

# Chunk each site artifact.
site_artifacts_chunks = [text_chunker.chunk(artifact) for artifact in site_artifacts]
# Flatten the list of chunks before inserting them into the vector store.
site_artifacts_chunks = [
    site_artifact_chunk for site_artifact_chunk in site_artifacts_chunks for site_artifact_chunk in site_artifact_chunk
]
vector_store.upsert_collection({"griptape": site_artifacts_chunks})

rag_engine = RagEngine(
    # This stage is responsible for producing the query. It can include things like translation, rewriting, etc.
    query_stage=QueryRagStage(query_modules=[TranslateQueryRagModule(prompt_driver=prompt_driver, language="english")]),
    # This stage is responsible for retrieving the relevant chunks.
    retrieval_stage=RetrievalRagStage(
        max_chunks=5,
        retrieval_modules=[  # Modules can pull from different sources.
            # Such as a vector store
            VectorStoreRetrievalRagModule(
                name="WebRetriever",
                vector_store_driver=vector_store,
                query_params={"top_n": 20, "namespace": "griptape"},
            ),
            # Or a text source.
            TextLoaderRetrievalRagModule(
                loader=TextLoader(),
                vector_store_driver=vector_store,
                source="README.md",
            ),
        ],
        # We can rerank the chunks before passing them to the response stage to ensure the best ones are used.
        rerank_module=TextChunksRerankRagModule(rerank_driver=LocalRerankDriver()),
    ),
    # This stage is responsible for generating the final response.
    response_stage=ResponseRagStage(
        response_modules=[
            # You can have multiple response modules to generate different types of responses.
            PromptResponseRagModule(
                prompt_driver=prompt_driver,
                rulesets=[Ruleset(name="Concise", rules=[Rule("Answer concisely")])],
            ),
            # This one generates a response with footnotes.
            FootnotePromptResponseRagModule(prompt_driver=prompt_driver),
            # This one just returns the text chunks directly with no LLM generation.
            TextChunksResponseRagModule(),
        ]
    ),
)

rag_context = RagContext(
    query="¿Qué ofrecen los servicios en la nube de Griptape?",  # What do Griptape's cloud services offer?
)
rag_context = rag_engine.process(rag_context)

# Let's print out the interesting responses
for output in rag_context.outputs[:2]:
    print(output.to_text() + "\n")

# We can also see the references that were configured up-front
pprint(rag_context.get_references())
