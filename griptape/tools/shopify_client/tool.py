from textwrap import dedent
from typing import Optional
from urllib.parse import urljoin
import schema
from schema import Schema, Literal
from attr import define, field
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact


@define
class ShopifyClient(BaseTool):
    storename: str = field(kw_only=True)
    storefront_access_token: str = field(kw_only=True)
    shopify_endpoint: str = field(default="myshopify.com/api/2023-07/graphql.json")

    @activity(
        config={
            "description": "Can be used to search for shopify products",
            "schema": Schema(
                {
                    Literal("first", description="How many products to retreive."): str,
                }
            ),
        }
    )
    def search(self, params: dict) -> BaseArtifact:
        from requests import post, exceptions

        first = params.get("first", 10)

        url = f"https://{self.storename}.{self.shopify_endpoint}"
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
                headers={
                    "X-Shopify-Storefront-Access-Token": self.storefront_access_token
                },
                timeout=30,
            )

            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))
