from textwrap import dedent
from typing import Union
from schema import Schema, Literal
from attr import define, field
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.artifacts import TextArtifact, ErrorArtifact


@define
class ShopifyClient(BaseTool):
    storename: str = field(kw_only=True)
    access_token: str = field(kw_only=True)
    schema_endpoint: str = field(
        kw_only=True, default="myshopify.com/api/2023-07/graphql.json"
    )
    timeout: int = field(kw_only=True, default=30)

    @activity(
        config={
            "description": "Can be used to search for Shopify products",
            "schema": Schema(
                {
                    Literal(
                        "product_count",
                        description="How many products to retrieve.",
                    ): str,
                }
            ),
        }
    )
    def search(self, params: dict) -> Union[list[TextArtifact], ErrorArtifact]:
        from requests import post, exceptions

        first = params.get("product_count", 10)

        url = f"https://{self.storename}.{self.schema_endpoint}"
        body = {
            "query": dedent(
                """
                        query getProducts($first: Int, $after: String) { 
                            products(first: $first, after: $after) { 
                                edges { 
                                    cursor node { 
                                        title 
                                    } 
                                },
                                pageInfo { 
                                    hasNextPage endCursor 
                                } 
                            } 
                        }
            """
            ),
            "variables": {"first": first},
        }

        try:
            response = post(
                url,
                json=body,
                headers={"X-Shopify-Storefront-Access-Token": self.access_token},
                timeout=self.timeout,
            )

            products = [
                TextArtifact(edge["node"]["title"])
                for edge in response.json()["data"]["products"]["edges"]
            ]
            return products
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))
