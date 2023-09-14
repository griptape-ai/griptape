import os
from pathlib import Path
from attr import define, field
from griptape import utils
from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseLoader


@define
class FileLoader(BaseLoader):
    dir_name: str = field(kw_only=True)

    def load(self, path: Path) -> list[BlobArtifact]:
        return self.text_to_artifacts(path)

    def load_collection(self, paths: list[Path]) -> dict[str, list[BlobArtifact]]:
        return utils.execute_futures_dict({
            utils.str_to_hash(str(path)): self.futures_executor.submit(self.text_to_artifacts, path)
            for path in paths
        })

    def text_to_artifacts(self, path: Path) -> list[BlobArtifact]:
        file_name = os.path.basename(path)

        with open(path, "rb") as file:
            body = file.read()

        return [BlobArtifact(body, name=file_name, dir=self.dir_name)]
