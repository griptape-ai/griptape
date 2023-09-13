import pandas as pd
from typing import Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class DataFrameLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)

    def load(self, dataframe: pd.DataFrame) -> list[CsvRowArtifact]:
        return self._load_file(dataframe)

    def load_collection(self, dataframes: list[pd.DataFrame]) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict({
            utils.dataframe_to_hash(dataframe): self.futures_executor.submit(self._load_file, dataframe)
            for dataframe in dataframes
        })

    def _load_file(self, dataframe: pd.DataFrame) -> list[CsvRowArtifact]:
        artifacts = []

        chunks = [CsvRowArtifact(row) for row in dataframe.to_dict(orient="records")]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts
