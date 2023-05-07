import os
import tempfile

from griptape.artifacts import BlobArtifact
from griptape.ramps import BlobManagerRamp
from tests.mocks.mock_tool.tool import MockTool


class TestBlobManagerRamp:
    def test_constructor(self):
        ramp = BlobManagerRamp(dir="/")

        assert ramp.name == "BlobManagerRamp"
        assert ramp.dir == "/"

        ramp = BlobManagerRamp(name="MyRamp")

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = BlobManagerRamp(name="MyRamp")

        output = ramp.process_output(MockTool().test, BlobArtifact("foo", value=b"foo"))

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" as blob'
        )

        assert ramp.blobs[0].name == "foo"

    def test_find_blob(self):
        ramp = BlobManagerRamp(name="MyRamp")
        artifact = BlobArtifact("foo", value=b"foo")

        ramp.add_blob(artifact)

        assert ramp.find_blob(artifact.name) == artifact

    def test_add_blob(self):
        ramp = BlobManagerRamp(name="MyRamp")
        artifact = BlobArtifact("foo", value=b"foo")

        ramp.add_blob(artifact)

        assert ramp.blobs[0] == artifact

    def test_save(self):
        with tempfile.TemporaryDirectory() as blob_dir:
            ramp = BlobManagerRamp(dir=blob_dir)
            artifact = BlobArtifact("foo.txt", dir="bar", value=b"foobar")

            ramp.add_blob(artifact)

            ramp.save({
                "current_ramp_path": "bar/foo.txt",
                "new_disk_path": "baz/foo.txt"
            })

            with open(os.path.join(blob_dir, "baz/foo.txt"), "rb") as file:
                assert file.read() == b"foobar"
