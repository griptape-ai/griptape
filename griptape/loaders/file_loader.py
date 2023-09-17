from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from attr import define, field
from griptape import utils
from griptape.artifacts import BlobArtifact, TextArtifact, ErrorArtifact
from griptape.loaders import BaseLoader


@define
class FileLoader(BaseLoader):
    workdir: str = field(default=os.getcwd(), kw_only=True)

    @workdir.validator
    def validate_workdir(self, _, workdir: str) -> None:
        if not Path(workdir).is_absolute():
            raise ValueError("workdir has to be absolute absolute")

    def load(self, path: Path, encoding: Optional[str] = None) -> TextArtifact | BlobArtifact | ErrorArtifact:
        return self.file_to_artifact(path, encoding)

    def load_collection(
            self, paths: list[Path], encoding: Optional[str] = None
    ) -> dict[str, TextArtifact | BlobArtifact | ErrorArtifact]:
        return utils.execute_futures_dict({
            utils.str_to_hash(
                str(path)
            ): self.futures_executor.submit(self.file_to_artifact, path, encoding)
            for path in paths
        })

    def file_to_artifact(self, path: Path, encoding: Optional[str]) -> TextArtifact | BlobArtifact | ErrorArtifact:
        full_path = os.path.join(self.workdir, path)
        file_name = os.path.basename(path)

        try:
            with open(full_path, "rb") as file:
                if encoding:
                    return TextArtifact(
                        file.read().decode(encoding),
                        name=file_name
                    )
                else:
                    return BlobArtifact(
                        file.read(),
                        name=file_name,
                        dir_name=os.path.dirname(path)
                    )
        except FileNotFoundError:
            return ErrorArtifact(f"file {file_name} not found")
        except Exception as e:
            return ErrorArtifact(f"error loading file: {e}")