import os
from pathlib import Path
from attr import define, field
from griptape import utils
from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseLoader


@define
class FileLoader(BaseLoader):
    workdir: str = field(default=os.getcwd(), kw_only=True)

    @workdir.validator
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("workdir has to be absolute absolute")

    def load(self, path: Path) -> BlobArtifact:
        return self.file_to_artifact(path)

    def load_collection(self, paths: list[Path]) -> dict[str, BlobArtifact]:
        return utils.execute_futures_dict({
            utils.str_to_hash(str(path)): self.futures_executor.submit(self.file_to_artifact, path)
            for path in paths
        })

    def file_to_artifact(self, path: Path) -> BlobArtifact:
        full_path = os.path.join(self.workdir, path)

        with open(full_path, "rb") as file:
            body = file.read()

        return BlobArtifact(
            body,
            name=os.path.basename(path),
            dir_name=str(os.path.dirname(path))
        )
