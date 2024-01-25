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

    def load(self, source: str, *args, **kwargs) -> list[CsvRowArtifact]:
        return self._load_file(source)

    def load_collection(self, sources: list[str], *args, **kwargs) -> dict[str, list[CsvRowArtifact]]:
        return utils.execute_futures_dict(
            {utils.str_to_hash(source): self.futures_executor.submit(self._load_file, source) for source in sources}
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
