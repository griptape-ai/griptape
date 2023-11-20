import os
import time
import requests
from typing import Optional
from attr import field, define, Factory
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver


@define
class LeonardoImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for the Leonardo image generation API.

    Attributes:
        model: The ID of the model to use when generating images.
        api_key: The API key to use when making requests to the Leonardo API.
        requests_session: The requests session to use when making requests to the Leonardo API.
        api_base: The base URL of the Leonardo API.
        max_attempts: The maximum number of times to poll the Leonardo API for a completed image.
        image_width: The width of the generated image in the range [32, 1024] and divisible by 8.
        image_height: The height of the generated image in the range [32, 1024] and divisible by 8.
        steps: Optionally specify the number of inference steps to run for each image generation request, [30, 60].
        seed: Optionally provide a consistent seed to generation requests, increasing consistency in output.

    Details on Leonardo image generation parameters can be found here:
    https://docs.leonardo.ai/reference/creategeneration
    """

    api_key: str = field(kw_only=True)
    requests_session: requests.Session = field(default=Factory(lambda: requests.Session()), kw_only=True)
    api_base: str = "https://cloud.leonardo.ai/api/rest/v1"
    max_attempts: int = field(default=10, kw_only=True)
    image_width: int = field(default=512, kw_only=True)
    image_height: int = field(default=512, kw_only=True)
    steps: Optional[int] = field(default=None, kw_only=True)
    seed: Optional[int] = field(default=None, kw_only=True)

    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        if negative_prompts is None:
            negative_prompts = []

        prompt = ", ".join(prompts)
        negative_prompt = ", ".join(negative_prompts)

        generation_id = self._create_generation(prompt=prompt, negative_prompt=negative_prompt)
        image_url = self._get_image_url(generation_id=generation_id)
        image_data = self._download_image(url=image_url)

        return ImageArtifact(
            value=image_data,
            mime_type="image/png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
            prompt=prompt,
        )

    def _create_generation(self, prompt: str, negative_prompt: str):
        request = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": self.image_width,
            "height": self.image_height,
            "num_images": 1,
            "modelId": self.model,
        }

        if self.steps is not None:
            request["num_inference_steps"] = self.steps

        if self.seed is not None:
            request["seed"] = self.seed

        response = self.requests_session.post(
            url=f"{self.api_base}/generations", headers={"Authorization": f"Bearer {self.api_key}"}, json=request
        ).json()

        return response["sdGenerationJob"]["generationId"]

    def _get_image_url(self, generation_id: str):
        for attempt in range(self.max_attempts):
            response = self.requests_session.get(
                url=f"{self.api_base}/generations/{generation_id}", headers={"Authorization": f"Bearer {self.api_key}"}
            ).json()

            if response["generations_by_pk"]["status"] == "PENDING":
                time.sleep(attempt + 1)
                continue

            return response["generations_by_pk"]["generated_images"][0]["url"]
        else:
            raise Exception("image generation failed to complete")

    def _download_image(self, url: str):
        response = self.requests_session.get(url=url, headers={"Authorization": f"Bearer {self.api_key}"})

        return response.content
