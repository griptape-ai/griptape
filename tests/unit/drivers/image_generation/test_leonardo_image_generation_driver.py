import uuid
from unittest.mock import Mock
import pytest
from griptape.drivers import LeonardoImageGenerationDriver


class TestLeonardoImageGenerationDriver:
    @pytest.fixture
    def driver(self):
        requests_session = Mock()

        return LeonardoImageGenerationDriver(api_key="test_api_key", requests_session=requests_session)

    def test_init(self, driver):
        assert driver

    def test_create_generation(self, driver):
        test_generation_id = str(uuid.uuid4())

        # Mock post request to create image generation
        driver.requests_session.post().json.return_value = {"sdGenerationJob": {"generationId": test_generation_id}}

        generation_id = driver._create_generation(prompt="test_prompt", negative_prompt="test_negative_prompt")

        assert generation_id == test_generation_id

    def test_get_image_url(self, driver):
        test_image_url = "test_image_url"

        # Mock get request to get image url
        driver.requests_session.get().json.return_value = {
            "generations_by_pk": {"status": "COMPLETE", "generated_images": [{"url": test_image_url}]}
        }

        image_url = driver._get_image_url(generation_id="generation_id")

        assert image_url == test_image_url

    def test_download_image(self, driver):
        test_image_data = b"test_image_data"

        # Mock get request to download image
        driver.requests_session.get().content = test_image_data

        image_data = driver._download_image(url="test_image_url")

        assert image_data == test_image_data

    def test_generate_image(self, driver):
        test_generation_id = str(uuid.uuid4())
        test_image_url = "test_image_url"

        driver._create_generation = Mock(return_value=test_generation_id)
        driver._get_image_url = Mock(return_value=test_image_url)
        driver._download_image = Mock(return_value=b"test_image_data")

        image_artifact = driver.generate_image(prompts=["test_prompt"], negative_prompts=["test_negative_prompt"])

        assert image_artifact.value == b"test_image_data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "leonardo/default"
        assert image_artifact.prompt == "test_prompt"
