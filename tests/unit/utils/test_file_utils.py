import pytest

from griptape.utils.file_utils import get_mime_type


class TestFileUtils:
    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        ("file_path_or_bytes", "expected"),
        [
            ("addresses.csv", "text/csv"),
            ("bad.asdf", "application/octet-stream"),
            ("bitcoin-2.pdf", "application/pdf"),
            ("bitcoin.pdf", "application/pdf"),
            ("cities.csv", "text/csv"),
            ("cow.png", "image/png"),
            ("foobar-many.txt", "text/plain"),
            ("griptape-comfyui.mp4", "video/mp4"),
            ("mountain-mask.png", "image/png"),
            ("mountain.jpg", "image/jpeg"),
            ("mountain.png", "image/png"),
            ("pig-balloon.jpg", "image/jpeg"),
            ("pig-balloon.png", "image/webp"),  # TODO: Unclear why detecting as webp
            ("sentences.wav", "audio/x-wav"),
            ("sentences2.wav", "audio/x-wav"),
            ("small.bmp", "image/bmp"),
            ("small.gif", "image/gif"),
            ("small.jpg", "image/jpeg"),
            ("small.png", "image/png"),
            ("small.tiff", "image/tiff"),
            ("small.webp", "image/webp"),
            ("test-1.csv", "text/csv"),
            ("test-2.csv", "text/csv"),
            ("test-pipe.csv", "text/csv"),
            ("test.json", "application/json"),
            ("test.txt", "text/plain"),
            ("test_ruleset.json", "application/json"),
        ],
    )
    def test_get_mime_type_file_path(self, path_from_resource_path, file_path_or_bytes, expected):
        data = path_from_resource_path(file_path_or_bytes)

        mime_type = get_mime_type(data)

        assert mime_type == expected

    @pytest.mark.parametrize(
        ("file_path_or_bytes", "expected"),
        [
            ("addresses.csv", "text/csv"),
            ("bad.asdf", "text/plain"),
            ("bitcoin-2.pdf", "application/pdf"),
            ("bitcoin.pdf", "application/pdf"),
            ("cities.csv", "text/csv"),
            ("cow.png", "image/png"),
            ("foobar-many.txt", "text/plain"),
            ("griptape-comfyui.mp4", "video/mp4"),
            ("mountain-mask.png", "image/png"),
            ("mountain.jpg", "image/jpeg"),
            ("mountain.png", "image/png"),
            ("pig-balloon.jpg", "image/jpeg"),
            ("pig-balloon.png", "image/webp"),  # TODO: Unclear why detecting as webp
            ("sentences.wav", "audio/x-wav"),
            ("sentences2.wav", "audio/x-wav"),
            ("small.bmp", "image/bmp"),
            ("small.gif", "image/gif"),
            ("small.jpg", "image/jpeg"),
            ("small.png", "image/png"),
            ("small.tiff", "image/tiff"),
            ("small.webp", "image/webp"),
            ("test-1.csv", "text/csv"),
            ("test-2.csv", "text/csv"),
            ("test-pipe.csv", "text/csv"),
            ("test.json", "application/json"),
            ("test.txt", "text/plain"),
            ("test_ruleset.json", "application/json"),
        ],
    )
    def test_get_mime_type_bytes(self, bytes_from_resource_path, file_path_or_bytes, expected):
        data = bytes_from_resource_path(file_path_or_bytes)

        mime_type = get_mime_type(data.read())

        assert mime_type == expected
