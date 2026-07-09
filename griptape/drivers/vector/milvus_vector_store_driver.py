from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any, cast

from attrs import Attribute, define, field

from griptape import utils
from griptape.artifacts import BaseArtifact
from griptape.drivers.vector import BaseVectorStoreDriver
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pymilvus import MilvusClient


DEFAULT_URI = "./milvus.db"
DEFAULT_METRIC_TYPE = "COSINE"
DEFAULT_ID_FIELD = "id"
DEFAULT_VECTOR_FIELD = "vector"
DEFAULT_TEXT_FIELD = "text"
DEFAULT_NAMESPACE_FIELD = "namespace"
DEFAULT_METADATA_FIELD = "metadata"
DEFAULT_ID_MAX_LENGTH = 512
DEFAULT_TEXT_MAX_LENGTH = 65535
DEFAULT_NAMESPACE_MAX_LENGTH = 512
SUPPORTED_METRIC_TYPES = {"COSINE", "IP", "L2"}
FIELD_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _normalize_metric_type(metric_type: str) -> str:
    return metric_type.upper()


@define
class MilvusVectorStoreDriver(BaseVectorStoreDriver):
    """A vector store driver for Milvus.

    Attributes:
        uri: Milvus connection URI. Defaults to a local Milvus Lite database.
        token: Optional token for authenticated Milvus deployments.
        db_name: Optional Milvus database name.
        collection_name: Name of the Milvus collection.
        vector_dim: Optional expected vector dimension. If omitted, the first upsert or query creates the collection with that vector size.
        metric_type: Vector metric for the Milvus index.
        consistency_level: Optional consistency level passed when creating the collection.
        id_field: Name of the primary key field.
        vector_field: Name of the vector field.
        text_field: Name of the stored text field.
        namespace_field: Name of the namespace field.
        metadata_field: Name of the JSON metadata field.
    """

    uri: str = field(default=DEFAULT_URI, kw_only=True, metadata={"serializable": True})
    token: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    db_name: str | None = field(default=None, kw_only=True, metadata={"serializable": True})
    collection_name: str = field(kw_only=True, metadata={"serializable": True})
    vector_dim: int | None = field(default=None, kw_only=True, metadata={"serializable": True})
    metric_type: str = field(
        default=DEFAULT_METRIC_TYPE,
        converter=_normalize_metric_type,
        kw_only=True,
        metadata={"serializable": True},
    )
    consistency_level: str | None = field(default=None, kw_only=True, metadata={"serializable": True})
    id_field: str = field(default=DEFAULT_ID_FIELD, kw_only=True, metadata={"serializable": True})
    vector_field: str = field(default=DEFAULT_VECTOR_FIELD, kw_only=True, metadata={"serializable": True})
    text_field: str = field(default=DEFAULT_TEXT_FIELD, kw_only=True, metadata={"serializable": True})
    namespace_field: str = field(default=DEFAULT_NAMESPACE_FIELD, kw_only=True, metadata={"serializable": True})
    metadata_field: str = field(default=DEFAULT_METADATA_FIELD, kw_only=True, metadata={"serializable": True})
    id_max_length: int = field(default=DEFAULT_ID_MAX_LENGTH, kw_only=True, metadata={"serializable": True})
    text_max_length: int = field(default=DEFAULT_TEXT_MAX_LENGTH, kw_only=True, metadata={"serializable": True})
    namespace_max_length: int = field(
        default=DEFAULT_NAMESPACE_MAX_LENGTH, kw_only=True, metadata={"serializable": True}
    )
    _client: MilvusClient | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @metric_type.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_metric_type(self, _: Attribute, metric_type: str) -> None:
        if metric_type not in SUPPORTED_METRIC_TYPES:
            raise ValueError(f"metric_type must be one of {sorted(SUPPORTED_METRIC_TYPES)}.")

    @lazy_property()
    def client(self) -> MilvusClient:
        pymilvus = utils.import_optional_dependency("pymilvus")
        client_kwargs = {"uri": self.uri}

        if self.token is not None:
            client_kwargs["token"] = self.token
        if self.db_name is not None:
            client_kwargs["db_name"] = self.db_name

        return pymilvus.MilvusClient(**client_kwargs)

    def setup(self, *, vector_dim: int | None = None) -> None:
        self._ensure_collection(vector_dim=vector_dim)

    def delete_vector(self, vector_id: str) -> None:
        if not self.client.has_collection(collection_name=self.collection_name):
            return

        self.client.delete(collection_name=self.collection_name, ids=[vector_id])

    def upsert_vector(
        self,
        vector: list[float],
        *,
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        content: str | None = None,
        **kwargs,
    ) -> str:
        vector_id = vector_id or utils.str_to_hash(str(vector))
        meta = meta or {}
        text = self._text_from_meta(meta, content=content)

        self._validate_string_length(vector_id, self.id_field, self.id_max_length)
        if namespace is not None:
            self._validate_string_length(namespace, self.namespace_field, self.namespace_max_length)
        self._validate_string_length(text, self.text_field, self.text_max_length)
        self._ensure_collection(vector_dim=len(vector))

        data = {
            self.id_field: vector_id,
            self.vector_field: vector,
            self.text_field: text,
            self.namespace_field: namespace,
            self.metadata_field: meta,
            **self._dynamic_fields_from_meta(meta),
        }
        data.update(kwargs)

        self.client.upsert(collection_name=self.collection_name, data=[data])

        return vector_id

    def load_entry(self, vector_id: str, *, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        if not self.client.has_collection(collection_name=self.collection_name):
            return None

        filter_expression = self._join_filter_clauses(
            [
                self._build_filter_clause(self.id_field, vector_id),
                self._build_filter_clause(self.namespace_field, namespace) if namespace is not None else None,
            ],
        )
        results = self.client.query(
            collection_name=self.collection_name,
            filter=filter_expression,
            output_fields=self._output_fields(include_vectors=True),
        )

        if not results:
            return None

        return self._entry_from_entity(results[0], include_vectors=True)

    def load_entries(self, *, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        if not self.client.has_collection(collection_name=self.collection_name):
            return []

        filter_expression = ""
        if namespace is not None:
            filter_expression = self._build_filter_clause(self.namespace_field, namespace)

        results = self.client.query(
            collection_name=self.collection_name,
            filter=filter_expression,
            output_fields=self._output_fields(include_vectors=True),
        )

        return [self._entry_from_entity(result, include_vectors=True) for result in results]

    def query_vector(
        self,
        vector: list[float],
        *,
        count: int | None = None,
        namespace: str | None = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.Entry]:
        self._ensure_collection(vector_dim=len(vector))

        filter_expression = self._build_filter_expression(namespace=namespace, query_filter=kwargs.pop("filter", None))
        results = self.client.search(
            collection_name=self.collection_name,
            data=[vector],
            filter=filter_expression,
            limit=count or BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
            output_fields=self._output_fields(include_vectors=include_vectors),
            anns_field=self.vector_field,
            search_params={"metric_type": self.metric_type},
            **kwargs,
        )

        return [
            self._entry_from_entity(
                match.get("entity", {}) | {self.id_field: match.get("id")},
                include_vectors=include_vectors,
                score=self._score_from_distance(match.get("distance")),
            )
            for match in results[0]
        ]

    def _ensure_collection(self, *, vector_dim: int | None = None) -> None:
        if self.vector_dim is not None and vector_dim is not None and self.vector_dim != vector_dim:
            raise ValueError(f"Expected vector dimension {self.vector_dim}, got {vector_dim}.")

        expected_vector_dim = vector_dim or self.vector_dim

        if self.client.has_collection(collection_name=self.collection_name):
            self._validate_collection(vector_dim=expected_vector_dim)
            return

        if expected_vector_dim is None:
            raise ValueError("vector_dim is required to create a Milvus collection.")

        pymilvus = utils.import_optional_dependency("pymilvus")
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(
            field_name=self.id_field,
            datatype=pymilvus.DataType.VARCHAR,
            is_primary=True,
            max_length=self.id_max_length,
        )
        schema.add_field(field_name=self.vector_field, datatype=pymilvus.DataType.FLOAT_VECTOR, dim=expected_vector_dim)
        schema.add_field(
            field_name=self.text_field,
            datatype=pymilvus.DataType.VARCHAR,
            max_length=self.text_max_length,
        )
        schema.add_field(
            field_name=self.namespace_field,
            datatype=pymilvus.DataType.VARCHAR,
            max_length=self.namespace_max_length,
            nullable=True,
        )
        schema.add_field(field_name=self.metadata_field, datatype=pymilvus.DataType.JSON, nullable=True)

        index_params = self.client.prepare_index_params()
        index_params.add_index(field_name=self.vector_field, index_type="AUTOINDEX", metric_type=self.metric_type)

        create_collection_kwargs: dict[str, Any] = {
            "collection_name": self.collection_name,
            "schema": schema,
            "index_params": index_params,
        }

        if self.consistency_level is not None:
            create_collection_kwargs["consistency_level"] = self.consistency_level

        self.client.create_collection(**create_collection_kwargs)

    def _validate_collection(self, *, vector_dim: int | None = None) -> None:
        pymilvus = utils.import_optional_dependency("pymilvus")
        collection = cast("dict[str, Any]", self.client.describe_collection(collection_name=self.collection_name))
        fields = {field["name"]: field for field in collection.get("fields", [])}

        required_fields = {
            self.id_field: pymilvus.DataType.VARCHAR,
            self.vector_field: pymilvus.DataType.FLOAT_VECTOR,
            self.text_field: pymilvus.DataType.VARCHAR,
            self.namespace_field: pymilvus.DataType.VARCHAR,
            self.metadata_field: pymilvus.DataType.JSON,
        }
        missing_fields = [field_name for field_name in required_fields if field_name not in fields]

        if missing_fields:
            raise ValueError(f"Milvus collection is missing required fields: {', '.join(missing_fields)}.")

        for field_name, expected_type in required_fields.items():
            if fields[field_name].get("type") != expected_type:
                raise ValueError(f"Milvus field {field_name!r} has an incompatible type.")

        if not fields[self.id_field].get("is_primary"):
            raise ValueError(f"Milvus field {self.id_field!r} must be the primary key.")

        existing_vector_dim = int(fields[self.vector_field]["params"]["dim"])
        if vector_dim is not None and existing_vector_dim != vector_dim:
            raise ValueError(f"Milvus collection vector dimension is {existing_vector_dim}, got {vector_dim}.")

    def _output_fields(self, *, include_vectors: bool) -> list[str]:
        output_fields = [self.id_field, self.text_field, self.namespace_field, self.metadata_field]

        if include_vectors:
            output_fields.append(self.vector_field)

        return output_fields

    def _entry_from_entity(
        self, entity: dict[str, Any], *, include_vectors: bool, score: float | None = None
    ) -> BaseVectorStoreDriver.Entry:
        return BaseVectorStoreDriver.Entry(
            id=str(entity[self.id_field]),
            vector=entity.get(self.vector_field) if include_vectors else None,
            score=score,
            meta=entity.get(self.metadata_field),
            namespace=entity.get(self.namespace_field),
        )

    def _score_from_distance(self, distance: float | None) -> float | None:
        if distance is None:
            return None
        if self.metric_type == "COSINE":
            return 1 - distance
        if self.metric_type == "L2":
            return -distance
        return distance

    def _build_filter_expression(self, *, namespace: str | None, query_filter: dict | None) -> str:
        if query_filter is not None and not isinstance(query_filter, dict):
            raise ValueError("Milvus filter must be a dictionary.")

        clauses = [self._build_filter_clause(self.namespace_field, namespace)] if namespace is not None else []

        if query_filter is not None:
            clauses.extend(self._build_filter_clause(field_name, value) for field_name, value in query_filter.items())

        return self._join_filter_clauses(clauses)

    def _build_filter_clause(self, field_name: str, value: Any) -> str:
        self._validate_filter_field_name(field_name)

        if isinstance(value, (list, tuple, set)):
            values = list(value)
            if not values:
                raise ValueError("Milvus filter lists cannot be empty.")
            if not all(self._is_supported_filter_value(item) for item in values):
                raise ValueError("Milvus filter lists can only contain strings, numbers, or booleans.")
            return f"{field_name} in [{', '.join(self._literal(item) for item in values)}]"

        if not self._is_supported_filter_value(value):
            raise ValueError("Milvus filters only support strings, numbers, booleans, or lists of those values.")

        return f"{field_name} == {self._literal(value)}"

    def _validate_filter_field_name(self, field_name: str) -> None:
        if not FIELD_NAME_RE.fullmatch(field_name):
            raise ValueError(f"Invalid Milvus filter field name: {field_name!r}.")

        if field_name in {self.vector_field, self.metadata_field}:
            raise ValueError(f"Milvus filtering is not supported for field {field_name!r}.")

    def _literal(self, value: str | float | bool) -> str:
        return json.dumps(value)

    def _join_filter_clauses(self, clauses: Sequence[str | None]) -> str:
        return " and ".join(clause for clause in clauses if clause)

    def _dynamic_fields_from_meta(self, meta: dict) -> dict[str, Any]:
        reserved_fields = {
            self.id_field,
            self.vector_field,
            self.text_field,
            self.namespace_field,
            self.metadata_field,
            "artifact",
        }

        return {
            field_name: value
            for field_name, value in meta.items()
            if field_name not in reserved_fields
            and FIELD_NAME_RE.fullmatch(field_name)
            and self._is_supported_filter_value(value)
        }

    def _is_supported_filter_value(self, value: Any) -> bool:
        return isinstance(value, (str, int, float, bool))

    def _text_from_meta(self, meta: dict, *, content: str | None = None) -> str:
        if content is not None:
            return content

        artifact = meta.get("artifact")
        if isinstance(artifact, str):
            try:
                return BaseArtifact.from_json(artifact).to_text()
            except Exception:
                return ""

        return ""

    def _validate_string_length(self, value: str, field_name: str, max_length: int) -> None:
        if len(value) > max_length:
            raise ValueError(f"Milvus field {field_name!r} cannot exceed {max_length} characters.")
