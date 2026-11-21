import uuid
from io import BytesIO
from unittest.mock import Mock

import pytest
import requests
from PIL import Image

from griptape.artifacts import BlobArtifact, ImageArtifact
from griptape.drivers.file_manager.local import LocalFileManagerDriver
from griptape.drivers.image_generation.leonardo import LeonardoImageGenerationDriver
from griptape.memory import TaskMemory
from griptape.memory.task.storage import BlobArtifactStorage
from griptape.tools import FileManagerTool, PromptImageGenerationTool


class TestLeonardoImageGenerationDriver:
    @pytest.fixture(autouse=True)
    def block_network(self, mocker):
        for target in (
            "requests.sessions.Session.request",
            "requests.post",
            "socket.create_connection",
            "socket.socket.connect",
            "socket.socket.connect_ex",
        ):
            mocker.patch(target, side_effect=AssertionError("Unexpected network access in Leonardo unit test"))
        mocker.patch(
            "griptape.tools.BaseTool.install_dependencies",
            side_effect=AssertionError("Unexpected dependency installation in Leonardo unit test"),
        )

    @pytest.fixture()
    def driver(self):
        requests_session = Mock(spec=requests.Session)

        return LeonardoImageGenerationDriver(
            api_key="test_api_key", requests_session=requests_session, model="test_model_id", max_attempts=1
        )

    @pytest.fixture()
    def download_response(self):
        def make_response(content, status_code=200, content_type="image/png"):
            response = requests.Response()
            response.status_code = status_code
            response.url = "https://images.example.test/test-image"
            if content_type is not None:
                response.headers["Content-Type"] = content_type
            response._content = content
            return response

        return make_response

    @pytest.fixture(params=["text_to_image", "image_variation", "prompt_tool"])
    def generate_image(self, request, driver, mocker, bytes_from_resource_path):
        driver.image_width = 32
        driver.image_height = 32
        initial_image = ImageArtifact(
            value=bytes_from_resource_path("small.png").getvalue(), format="png", width=32, height=32
        )
        upload_image = mocker.patch.object(
            LeonardoImageGenerationDriver, "_upload_init_image", return_value="test_init_image_id"
        )

        def generate(response):
            generation_response = Mock(ok=True)
            generation_response.json.return_value = {"sdGenerationJob": {"generationId": "test_generation_id"}}
            polling_response = Mock()
            polling_response.json.return_value = {
                "generations_by_pk": {
                    "status": "COMPLETE",
                    "generated_images": [{"url": response.url}],
                }
            }
            driver.requests_session.request.return_value = generation_response
            driver.requests_session.get.side_effect = [polling_response, response]

            prompts = ["test_prompt", "second_prompt"]
            negative_prompts = ["test_negative_prompt"]
            if request.param == "image_variation":
                artifact = driver.run_image_variation(
                    prompts=prompts, image=initial_image, negative_prompts=negative_prompts
                )
                upload_image.assert_called_once_with(initial_image)
            else:
                if request.param == "prompt_tool":
                    tool = PromptImageGenerationTool(image_generation_driver=driver, install_dependencies_on_init=False)
                    artifact = tool.generate_image(
                        {"values": {"prompt": ", ".join(prompts), "negative_prompt": ", ".join(negative_prompts)}}
                    )
                else:
                    artifact = driver.run_text_to_image(prompts=prompts, negative_prompts=negative_prompts)
                upload_image.assert_not_called()

            expected_request = {
                "prompt": "test_prompt, second_prompt",
                "negative_prompt": "test_negative_prompt",
                "width": 32,
                "height": 32,
                "num_images": 1,
                "modelId": "test_model_id",
            }
            if request.param == "image_variation":
                expected_request["init_image_id"] = "test_init_image_id"
            assert driver.requests_session.request.call_args.kwargs["json"] == expected_request
            assert driver.requests_session.get.call_count == 2
            return artifact

        return generate

    def test_init(self, driver):
        assert driver

    def test_create_generation(self, driver):
        test_generation_id = str(uuid.uuid4())

        generation_id = self._test_create_generation(driver=driver, test_generation_id=test_generation_id)

        assert generation_id == test_generation_id

    def _test_create_generation(self, driver, test_generation_id):
        # Mock post request to create image generation
        response = Mock()
        response.ok = True
        response.json.return_value = {"sdGenerationJob": {"generationId": test_generation_id}}
        driver.requests_session.request.return_value = response

        return driver._create_generation(prompts=["test_prompt"], negative_prompts=["test_negative_prompt"])

    def test_get_image_url(self, driver):
        test_image_url = "test_image_url"

        image_url = self._test_get_image_url(driver=driver, test_image_url=test_image_url)

        assert image_url == test_image_url

    def _test_get_image_url(self, driver, test_image_url):
        # Mock get request to get image url
        driver.requests_session.get().json.return_value = {
            "generations_by_pk": {"status": "COMPLETE", "generated_images": [{"url": test_image_url}]}
        }

        return driver._get_image_url(generation_id="generation_id")

    def test_download_image(self, driver, bytes_from_resource_path):
        test_image_data = bytes_from_resource_path("small.png").getvalue()

        image_data = self._test_download_image(driver=driver, test_image_data=test_image_data)

        assert image_data == test_image_data
        driver.requests_session.get.return_value.raise_for_status.assert_called_once_with()

    def _test_download_image(self, driver, test_image_data):
        # Mock get request to download image
        driver.requests_session.get().content = test_image_data

        return driver._download_image(url="test_image_url")

    def test_try_text_to_image(self, driver, bytes_from_resource_path):
        test_generation_id = str(uuid.uuid4())
        test_image_url = "test_image_url"
        test_image_data = bytes_from_resource_path("small.png").getvalue()

        self._test_create_generation(driver=driver, test_generation_id=test_generation_id)
        self._test_get_image_url(driver=driver, test_image_url=test_image_url)
        self._test_download_image(driver=driver, test_image_data=test_image_data)

        image_artifact = driver.try_text_to_image(prompts=["test_prompt"], negative_prompts=["test_negative_prompt"])

        assert image_artifact.value == test_image_data
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.meta["model"] == "test_model_id"
        assert image_artifact.meta["prompt"] == "test_prompt"

    @pytest.mark.parametrize("status_code", [403, 404, 500])
    def test_generation_rejects_download_http_errors(self, generate_image, download_response, status_code):
        response = download_response(
            b'{"error": "image download failed"}', status_code=status_code, content_type="application/json"
        )

        with pytest.raises(requests.HTTPError) as error:
            generate_image(response)

        assert error.value.response is response

    @pytest.mark.parametrize(
        "content",
        [
            b"",
            b"<html>Image unavailable</html>",
            b'{"error": "image unavailable"}',
            b"\x00\x01\x02\x03",
            b"%PDF-1.7\n%%EOF",
        ],
        ids=["empty", "html", "json", "unknown-binary", "pdf"],
    )
    def test_generation_rejects_non_image_success(self, generate_image, download_response, content):
        with pytest.raises(ValueError, match="did not contain a recognized image"):
            generate_image(download_response(content, content_type="image/png"))

    @pytest.mark.parametrize(("resource_path", "source_format"), [("small.png", "PNG"), ("small.jpg", "JPEG")])
    @pytest.mark.parametrize("content_type", ["image/png", "application/octet-stream", None])
    def test_generation_image_format_matches_bytes(
        self, generate_image, download_response, bytes_from_resource_path, resource_path, source_format, content_type
    ):
        image_data = bytes_from_resource_path(resource_path).getvalue()
        with Image.open(BytesIO(image_data)) as source:
            source.load()
            assert source.format == source_format

        response = download_response(image_data, content_type=content_type)
        artifact = generate_image(response)

        assert artifact.value == image_data
        with Image.open(BytesIO(artifact.value)) as image:
            image.load()
            assert image.format == source_format
            assert artifact.format == image.format.lower()
            assert artifact.mime_type == Image.MIME[image.format]
            assert artifact.width == image.width == 32
            assert artifact.height == image.height == 32

        assert artifact.name.endswith(f".{artifact.format}")
        assert artifact.meta["model"] == "test_model_id"
        assert artifact.meta["prompt"] == "test_prompt, second_prompt"

    @pytest.mark.parametrize("resource_path", ["small.png", "small.jpg"])
    def test_generation_memory_save_preserves_bytes(
        self, generate_image, download_response, bytes_from_resource_path, resource_path, tmp_path
    ):
        image_data = bytes_from_resource_path(resource_path).getvalue()
        artifact = generate_image(download_response(image_data))
        memory = TaskMemory(name="ImageMemory", artifact_storages={BlobArtifact: BlobArtifactStorage()})
        memory.store_artifact("generated-image", artifact)
        file_manager = FileManagerTool(
            input_memory=[memory],
            file_manager_driver=LocalFileManagerDriver(workdir=str(tmp_path)),
            install_dependencies_on_init=False,
        )

        result = file_manager.save_memory_artifacts_to_disk(
            {
                "values": {
                    "dir_name": "",
                    "file_name": "dog.png",
                    "memory_name": memory.name,
                    "artifact_namespace": "generated-image",
                }
            }
        )

        assert result.value == "Successfully saved memory artifacts to disk"
        saved_data = (tmp_path / "dog.png").read_bytes()
        assert saved_data == artifact.value == image_data
        with Image.open(BytesIO(saved_data)) as image:
            image.load()
            assert image.size == (32, 32)
            assert image.format.lower() == artifact.format
            assert Image.MIME[image.format] == artifact.mime_type
