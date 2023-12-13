from __future__ import annotations
import hashlib
from typing import Optional, TYPE_CHECKING
import pandas as pd
from attr import define, field
from griptape import utils
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from pandas import DataFrame


@define
class DataFrameLoader(BaseLoader):
    embedding_driver: BaseEmbeddingDriver | None = field(default=None, kw_only=True)

    def load(self, dataframe: DataFrame) -> list[CsvRowArtifact]:
        return self._load_file(dataframe)

    def load_collection(self, dataframes: list[DataFrame]) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {
                self._dataframe_to_hash(dataframe): self.futures_executor.submit(self._load_file, dataframe)
                for dataframe in dataframes
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
        return hashlib.sha256(pd.util.hash_pandas_object(dataframe, index=True).values).hexdigest()
