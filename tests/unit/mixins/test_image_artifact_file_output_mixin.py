import os
import tempfile

import pytest

from griptape.artifacts import ImageArtifact
from griptape.mixins.artifact_file_output_mixin import ArtifactFileOutputMixin


class TestArtifactFileOutputMixin:
    def test_no_output(self):
        class Test(ArtifactFileOutputMixin):
            pass

        assert Test().output_file is None
        assert Test().output_dir is None

    def test_output_file(self):
        artifact = ImageArtifact(name="test.png", value=b"test", height=1, width=1, format="png")

        class Test(ArtifactFileOutputMixin):
            def run(self) -> None:
                self._write_to_file(artifact)

        outfile = os.path.join(tempfile.gettempdir(), artifact.name)
        t = Test(output_file=outfile)
        t.run()

        assert t.output_file == outfile
        assert t.output_dir is None
        assert os.path.exists(outfile)

    def test_output_dir(self):
        artifact = ImageArtifact(name="test.png", value=b"test", height=1, width=1, format="png")

        class Test(ArtifactFileOutputMixin):
            def run(self) -> None:
                self._write_to_file(artifact)

        outdir = tempfile.gettempdir()
        t = Test(output_dir=outdir)
        t.run()

        assert t.output_file is None
        assert t.output_dir == outdir
        assert os.path.exists(os.path.join(outdir, artifact.name))

    def test_output_file_and_dir(self):
        class Test(ArtifactFileOutputMixin):
            pass

        outfile = "test.txt"
        outdir = "test"
        with pytest.raises(ValueError):
            Test(output_file=outfile, output_dir=outdir)
