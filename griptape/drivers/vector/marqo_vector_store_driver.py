from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseVectorStoreDriver
from griptape.artifacts import TextArtifact
from attr import define, field, Factory

if TYPE_CHECKING:
    import marqo


@define
class MarqoVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for Marqo.

    Attributes:
        api_key: The API key for the Marqo API.
        url: The URL to the Marqo API.
        mq: An optional Marqo client. Defaults to a new client with the given URL and API key.
        index: The name of the index to use.
    """

    api_key: str = field(kw_only=True)
    url: str = field(kw_only=True)
    mq: marqo.Client | None = field(
        default=Factory(
            lambda self: import_optional_dependency("marqo").Client(self.url, api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    index: str = field(kw_only=True)

    def upsert_text(
        self,
        string: str,
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        """Upsert a text document into the Marqo index.

        Args:
            string: The string to be indexed.
            vector_id: The ID for the vector. If None, Marqo will generate an ID.
            namespace: An optional namespace for the document.
            meta: An optional dictionary of metadata for the document.

        Returns:
            str: The ID of the document that was added.
        """

        doc = {"_id": vector_id, "Description": string}  # Description will be treated as tensor field

        # Non-tensor fields
        if meta:
            doc["meta"] = str(meta)
        if namespace:
            doc["namespace"] = namespace

        response = self.mq.index(self.index).add_documents([doc], tensor_fields=["Description"])
        return response["items"][0]["_id"]

    def upsert_text_artifact(
        self, artifact: TextArtifact, namespace: str | None = None, meta: dict | None = None, **kwargs
    ) -> str:
        """Upsert a text artifact into the Marqo index.

        Args:
            artifact: The text artifact to be indexed.
            namespace: An optional namespace for the artifact.
            meta: An optional dictionary of metadata for the artifact.

        Returns:
            str: The ID of the artifact that was added.
        """

        artifact_json = artifact.to_json()

        doc = {
            "_id": artifact.id,
            "Description": artifact.value,  # Description will be treated as tensor field
            "artifact": str(artifact_json),
            "namespace": namespace,
        }

        response = self.mq.index(self.index).add_documents([doc], tensor_fields=["Description", "artifact"])
        return response["items"][0]["_id"]

    def load_entry(self, vector_id: str, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        """Load a document entry from the Marqo index.

        Args:
            vector_id: The ID of the vector to load.
            namespace: The namespace of the vector to load.

        Returns:
            The loaded Entry if found, otherwise None.
        """
        result = self.mq.index(self.index).get_document(document_id=vector_id, expose_facets=True)

        if result and "_tensor_facets" in result and len(result["_tensor_facets"]) > 0:
            return BaseVectorStoreDriver.Entry(
                id=result["_id"],
                meta={k: v for k, v in result.items() if k not in ["_id"]},
                vector=result["_tensor_facets"][0]["_embedding"],
            )
        else:
            return None

    def load_entries(self, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        """Load all document entries from the Marqo index.

        Args:
            namespace: The namespace to filter entries by.

        Returns:
            The list of loaded Entries.
        """

        filter_string = f"namespace:{namespace}" if namespace else None
        results = self.mq.index(self.index).search("", limit=10000, filter_string=filter_string)

        # get all _id's from search results
        ids = [r["_id"] for r in results["hits"]]

        # get documents corresponding to the ids
        documents = self.mq.index(self.index).get_documents(document_ids=ids, expose_facets=True)

        # for each document, if it's found, create an Entry object
        entries = []
        for doc in documents["results"]:
            if doc["_found"]:
                entries.append(
                    BaseVectorStoreDriver.Entry(
                        id=doc["_id"],
                        vector=doc["_tensor_facets"][0]["_embedding"],
                        meta={k: v for k, v in doc.items() if k not in ["_id", "_tensor_facets", "_found"]},
                        namespace=doc.get("namespace"),
                    )
                )

        return entries

    def query(
        self,
        query: str,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        include_metadata: bool = True,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Query the Marqo index for documents.

        Args:
            query: The query string.
            count: The maximum number of results to return.
            namespace: The namespace to filter results by.
            include_vectors: Whether to include vector data in the results.
            include_metadata: Whether to include metadata in the results.

        Returns:
            The list of query results.
        """

        params = {
            "limit": count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
            "attributes_to_retrieve": ["*"] if include_metadata else ["_id"],
            "filter_string": f"namespace:{namespace}" if namespace else None,
        } | kwargs

        results = self.mq.index(self.index).search(query, **params)

        if include_vectors:
            results["hits"] = [
                {**r, **self.mq.index(self.index).get_document(r["_id"], expose_facets=True)} for r in results["hits"]
            ]

        return [
            BaseVectorStoreDriver.QueryResult(
                id=r["_id"],
                vector=r["_tensor_facets"][0]["_embedding"] if include_vectors else [],
                score=r["_score"],
                meta={k: v for k, v in r.items() if k not in ["_score", "_tensor_facets"]},
            )
            for r in results["hits"]
        ]

    def create_index(self, name: str, **kwargs) -> dict[str, Any]:
        """Create a new index in the Marqo client.

        Args:
            name: The name of the new index.
        """

        return self.mq.create_index(name, settings_dict=kwargs)

    def delete_index(self, name: str) -> dict[str, Any]:
        """Delete an index in the Marqo client.

        Args:
            name: The name of the index to delete.
        """

        return self.mq.delete_index(name)

    def get_indexes(self) -> list[str]:
        """Get a list of all indexes in the Marqo client.

        Returns:
            The list of all indexes.
        """

        # Change this once API issue is fixed (entries in results are no longer objects but dicts)
        return [index.index_name for index in self.mq.get_indexes()["results"]]

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        """Upsert a vector into the Marqo index.

        Args:
            vector: The vector to be indexed.
            vector_id: The ID for the vector. If None, Marqo will generate an ID.
            namespace: An optional namespace for the vector.
            meta: An optional dictionary of metadata for the vector.

        Raises:
            Exception: This function is not yet implemented.

        Returns:
            The ID of the vector that was added.
        """

        raise Exception("not implemented")
