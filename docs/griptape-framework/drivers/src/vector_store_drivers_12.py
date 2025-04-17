import os

from griptape.drivers.vector.pgai import PgAiKnowledgeBaseVectorStoreDriver

# PG.AI connection parameters
connection_string = os.environ["PGAI_CONNECTION_STRING"]
knowledge_base_name = os.environ["PGAI_KNOWLEDGE_BASE_NAME"]

vector_store_driver = PgAiKnowledgeBaseVectorStoreDriver(
    connection_string=connection_string,
    knowledge_base_name=knowledge_base_name,  # optional
)

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
