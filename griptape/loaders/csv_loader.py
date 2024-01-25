import csv
from typing import Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import CsvRowArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader


@define
class CsvLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    delimiter: str = field(default=",", kw_only=True)

    def load(self, filename: str) -> list[CsvRowArtifact]:
        return self._load_file(filename)

    def load_collection(self, filenames: list[str]) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {
                utils.str_to_hash(filename): self.futures_executor.submit(self._load_file, filename)
                for filename in filenames
            }
        )

    def _load_file(self, filename: str) -> list[CsvRowArtifact]:
        artifacts = []

        with open(filename, encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=self.delimiter)
            chunks = [CsvRowArtifact(row) for row in reader]

            if self.embedding_driver:
                for chunk in chunks:
                    chunk.generate_embedding(self.embedding_driver)

            for chunk in chunks:
                artifacts.append(chunk)

        return artifacts
