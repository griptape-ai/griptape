import uuid
from unittest.mock import Mock, PropertyMock, MagicMock
import pytest
from griptape.drivers import LeonardoImageGenerationDriver


class TestLeonardoImageGenerationDriver:
    @pytest.fixture
    def driver(self):
        requests_session = Mock()

        return LeonardoImageGenerationDriver(
            api_key="test_api_key", requests_session=requests_session, model="test_model_id"
        )

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

    def test_download_image(self, driver):
        test_image_data = b"test_image_data"

        image_data = self._test_download_image(driver=driver, test_image_data=test_image_data)

        assert image_data == test_image_data

    def _test_download_image(self, driver, test_image_data):
        # Mock get request to download image
        driver.requests_session.get().content = test_image_data

        return driver._download_image(url="test_image_url")

    def test_try_text_to_image(self, driver):
        test_generation_id = str(uuid.uuid4())
        test_image_url = "test_image_url"

        self._test_create_generation(driver=driver, test_generation_id=test_generation_id)
        self._test_get_image_url(driver=driver, test_image_url=test_image_url)
        self._test_download_image(driver=driver, test_image_data=b"test_image_data")

        image_artifact = driver.try_text_to_image(prompts=["test_prompt"], negative_prompts=["test_negative_prompt"])

        assert image_artifact.value == b"test_image_data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "test_model_id"
        assert image_artifact.prompt == "test_prompt"
