from __future__ import annotations

import json
import time
from typing import Literal, Optional

import requests
from attrs import Factory, define, field

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver


@define
class LeonardoImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for the Leonardo image generation API.

    Details on Leonardo image generation parameters can be found here:
    https://docs.leonardo.ai/reference/creategeneration

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
        init_strength: Optionally specify the strength of the initial image, [0.0, 1.0].
    """

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    requests_session: requests.Session = field(default=Factory(lambda: requests.Session()), kw_only=True)
    api_base: str = "https://cloud.leonardo.ai/api/rest/v1"
    max_attempts: int = field(default=10, kw_only=True, metadata={"serializable": True})
    image_width: int = field(default=512, kw_only=True, metadata={"serializable": True})
    image_height: int = field(default=512, kw_only=True, metadata={"serializable": True})
    steps: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    seed: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    init_strength: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    control_net: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    control_net_type: Optional[Literal["POSE", "CANNY", "DEPTH"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        if negative_prompts is None:
            negative_prompts = []

        generation_id = self._create_generation(prompts=prompts, negative_prompts=negative_prompts)
        image_url = self._get_image_url(generation_id=generation_id)
        image_data = self._download_image(url=image_url)

        return ImageArtifact(
            value=image_data,
            format="png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
            prompt=", ".join(prompts),
        )

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        if negative_prompts is None:
            negative_prompts = []

        init_image_id = self._upload_init_image(image)
        generation_id = self._create_generation(
            prompts=prompts,
            negative_prompts=negative_prompts,
            init_image_id=init_image_id,
        )
        image_url = self._get_image_url(generation_id=generation_id)
        image_data = self._download_image(url=image_url)

        return ImageArtifact(
            value=image_data,
            format="png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
            prompt=", ".join(prompts),
        )

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support outpainting")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support inpainting")

    def _upload_init_image(self, image: ImageArtifact) -> str:
        request = {"extension": image.mime_type.split("/")[1]}

        prep_response = self._make_api_request("/init-image", request=request)
        if prep_response is None or prep_response["uploadInitImage"] is None:
            raise Exception(f"failed to prepare init image: {prep_response}")

        fields = json.loads(prep_response["uploadInitImage"]["fields"])
        pre_signed_url = prep_response["uploadInitImage"]["url"]
        init_image_id = prep_response["uploadInitImage"]["id"]

        files = {"file": image.value}
        upload_response = requests.post(pre_signed_url, data=fields, files=files)
        if not upload_response.ok:
            raise Exception(f"failed to upload init image: {upload_response.text}")

        return init_image_id

    def _create_generation(
        self,
        prompts: list[str],
        negative_prompts: list[str],
        init_image_id: Optional[str] = None,
    ) -> str:
        prompt = ", ".join(prompts)
        negative_prompt = ", ".join(negative_prompts)
        request = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": self.image_width,
            "height": self.image_height,
            "num_images": 1,
            "modelId": self.model,
        }

        if init_image_id is not None:
            request["init_image_id"] = init_image_id

        if self.init_strength is not None:
            request["init_strength"] = self.init_strength

        if self.steps:
            request["num_inference_steps"] = self.steps

        if self.seed is not None:
            request["seed"] = self.seed

        if self.control_net:
            request["controlNet"] = self.control_net
            request["controlNetType"] = self.control_net_type

        response = self._make_api_request("/generations", request=request)
        if response is None or response["sdGenerationJob"] is None:
            raise Exception(f"failed to create generation: {response}")

        return response["sdGenerationJob"]["generationId"]

    def _make_api_request(self, endpoint: str, request: dict, method: str = "POST") -> dict:
        url = f"{self.api_base}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = self.requests_session.request(url=url, method=method, json=request, headers=headers)
        if not response.ok:
            raise Exception(f"failed to make API request: {response.text}")

        return response.json()

    def _get_image_url(self, generation_id: str) -> str:
        for attempt in range(self.max_attempts):
            response = self.requests_session.get(
                url=f"{self.api_base}/generations/{generation_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            ).json()

            if response["generations_by_pk"]["status"] == "PENDING":
                time.sleep(attempt + 1)
                continue

            return response["generations_by_pk"]["generated_images"][0]["url"]
        else:
            raise Exception("image generation failed to complete")

    def _download_image(self, url: str) -> bytes:
        response = self.requests_session.get(url=url, headers={"Authorization": f"Bearer {self.api_key}"})

        return response.content
