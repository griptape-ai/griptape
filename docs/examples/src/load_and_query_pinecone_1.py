import hashlib
import json
import os
from urllib.request import urlopen

from griptape.drivers import OpenAiEmbeddingDriver, PineconeVectorStoreDriver


def load_data(driver: PineconeVectorStoreDriver) -> None:
    response = urlopen(
        "https://raw.githubusercontent.com/wedeploy-examples/" "supermarket-web-example/master/products.json"
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


vector_driver = PineconeVectorStoreDriver(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT"],
    index_name=os.environ["PINECONE_INDEX_NAME"],
    embedding_driver=OpenAiEmbeddingDriver(),
)

load_data(vector_driver)

result = vector_driver.query(
    "fruit",
    count=3,
    filter={"price": {"$lte": 15}, "rating": {"$gte": 4}},
    namespace="supermarket-products",
)
print(result)
