from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from attr import define, field

from griptape import utils
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from pandas import DataFrame


@define
class DataFrameLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, source: DataFrame, *args, **kwargs) -> list[CsvRowArtifact]:
        return self._load_file(source)

    def load_collection(self, sources: list[DataFrame], *args, **kwargs) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {
                self._dataframe_to_hash(source): self.futures_executor.submit(self._load_file, source)
                for source in sources
            }
        )

    def _load_file(self, dataframe: DataFrame) -> list[CsvRowArtifact]:
        artifacts = []

        chunks = [CsvRowArtifact(row) for row in dataframe.to_dict(orient="records")]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def _dataframe_to_hash(self, dataframe: DataFrame) -> str:
        hash_pandas_object = import_optional_dependency("pandas.core.util.hashing").hash_pandas_object

        return utils.str_to_hash(str(hash_pandas_object(dataframe, index=True).values))
