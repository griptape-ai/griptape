import re


class TestVectorStores:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/vector-stores/
    """

    def test_local_vector_store(self):
        from griptape.artifacts import BaseArtifact
        from griptape.drivers import LocalVectorStoreDriver
        from griptape.loaders import WebLoader

        vector_store_driver = LocalVectorStoreDriver()
        artifacts = WebLoader(max_tokens=100).load("https://www.griptape.ai")

        [
            vector_store_driver.upsert_text_artifact(a, namespace="griptape")
            for a in artifacts
        ]

        results = vector_store_driver.query("creativity", count=3, namespace="griptape")

        values = [BaseArtifact.from_json(r.meta["artifact"]).value for r in results]

        result = "\n\n".join(values)

        assert re.search("tape", result, re.IGNORECASE)

    def test_pinecone_vector_store(self):
        import os
        import hashlib
        import json
        from urllib.request import urlopen
        from griptape.drivers import PineconeVectorStoreDriver

        def load_data(driver: PineconeVectorStoreDriver) -> None:
            response = urlopen(
                "https://raw.githubusercontent.com/wedeploy-examples/"
                "supermarket-web-example/master/products.json"
            )

            for product in json.loads(response.read()):
                driver.upsert_text(
                    product["description"],
                    vector_id=hashlib.md5(product["title"].encode()).hexdigest(),
                    meta={
                        "title": product["title"],
                        "description": product["description"],
                        "type": product["type"],
                        "price": product["price"],
                        "rating": product["rating"],
                    },
                    namespace="supermarket-products",
                )

        vector_store_driver = PineconeVectorStoreDriver(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT"),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
        )

        load_data(vector_store_driver)

        result = vector_store_driver.query(
            "fruit",
            count=3,
            filter={"price": {"$lte": 15}, "rating": {"$gte": 4}},
            namespace="supermarket-products",
        )

        assert result[0] is not None
        assert result[0].meta is not None
        assert re.search("cherry", result[0].meta["title"], re.IGNORECASE)

    def test_marqo_vector_store(self):
        import os
        from griptape.drivers import MarqoVectorStoreDriver
        from griptape.engines import VectorQueryEngine
        from griptape.loaders import WebLoader
        from griptape.tools import VectorStoreClient

        # Define the namespace
        namespace = "griptape-ai"

        # Initialize the vector store driver
        vector_store = MarqoVectorStoreDriver(
            api_key=os.getenv("MARQO_API_KEY"),
            url=os.getenv("MARQO_URL"),
            index=os.getenv("MARQO_INDEX_NAME"),
        )

        # Initialize the query engine
        query_engine = VectorQueryEngine(vector_store_driver=vector_store)

        # Initialize the knowledge base tool
        VectorStoreClient(
            description="Contains information about the Griptape Framework from www.griptape.ai",
            query_engine=query_engine,
            namespace=namespace,
        )

        # Load artifacts from the web
        artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

        # Upsert the artifacts into the vector store
        vector_store.upsert_text_artifacts(
            {
                namespace: artifacts,
            }
        )
        result = vector_store.query(query="What is griptape?")

        assert result[0] is not None

    def test_mongodb_atlas_vector_store(self):
        from griptape.drivers import MongoDbAtlasVectorStoreDriver
        from griptape.loaders import WebLoader
        import os

        host = os.getenv("MONGODB_HOST")
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")
        database_name = os.getenv("MONGODB_DATABASE_NAME")
        collection_name = os.getenv("MONGODB_COLLECTION_NAME")
        # Initialize the vector store driver
        vector_store = MongoDbAtlasVectorStoreDriver(
            connection_string=f"mongodb+srv://{username}:{password}@{host}/{database_name}",
            database_name=database_name,
            collection_name=collection_name,
        )

        # Load artifacts from the web
        artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

        # Upsert the artifacts into the vector store
        vector_store.upsert_text_artifacts(
            {
                "griptape": artifacts,
            }
        )

        result = vector_store.query(query="What is griptape?")

        assert result[0] is not None

    def test_redis_vector_store(self):
        import os
        from griptape.drivers import RedisVectorStoreDriver
        from griptape.loaders import WebLoader
        import numpy as np  # Assuming you'd use numpy to create a dummy vector for the sake of example.

        vector_store_driver = RedisVectorStoreDriver(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            password=os.getenv("REDIS_PASSWORD"),
            index=os.getenv("REDIS_INDEX"),
        )

        # Load artifacts from the web
        artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

        # Upsert the artifacts into the vector store
        vector_store_driver.upsert_text_artifacts(
            {
                "griptape": artifacts,
            }
        )

        result = vector_store_driver.query(query="What is griptape?")

        assert result[0] is not None

    def test_amazon_opensearch_vector_store(self):
        import os
        import boto3
        from griptape.drivers import AmazonOpenSearchVectorStoreDriver
        from griptape.loaders import WebLoader

        vector_store_driver = AmazonOpenSearchVectorStoreDriver(
            host=os.getenv("AMAZON_OPENSEARCH_HOST"),
            index_name=os.getenv("AMAZON_OPENSEARCH_INDEX_NAME"),
            session=boto3.Session(),
        )

        # vector_store_driver.create_index(vector_dimension=1536)
        # Load artifacts from the web
        artifacts = WebLoader(max_tokens=200).load("https://www.griptape.ai")

        # Upsert the artifacts into the vector store
        vector_store_driver.upsert_text_artifacts(
            {
                "griptape": artifacts,
            }
        )

        result = vector_store_driver.query(query="What is griptape?")

        assert result[0] is not None
