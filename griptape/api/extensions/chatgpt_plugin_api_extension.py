from __future__ import annotations
import json
from typing import Callable, TYPE_CHECKING
import yaml
from fastapi import FastAPI
from griptape.api.extensions import BaseApiExtension
from attr import define
from starlette.responses import Response
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.api import ToolApiGenerator


@define
class ChatGptPluginApiExtension(BaseApiExtension):
    class YAMLResponse(Response):
        media_type = "text/yaml"

    OPENAI_TEMPLATE_PATH = "tools/chat_gpt_plugin_manifest.json.j2"
    OPENAPI_SPEC_FILE = "openapi.yaml"
    LOGO_FILE = "logo.png"

    def __attrs_post_init__(self) -> None:
        self.route_fns.append(self.generate_manifest_route)
        self.route_fns.append(self.generate_spec_route)

    def generate_manifest_route(self, generator: ToolApiGenerator) -> dict:
        return {
            "path": f"/{self.OPENAI_TEMPLATE_PATH}",
            "endpoint": self._generate_manifest_fn(generator),
            "methods": ["GET"],
            "operation_id": "OpenAPIManifest",
            "description": "ChatGPT plugin manifest"
        }

    def generate_spec_route(self, generator: ToolApiGenerator) -> dict:
        return {
            "path": f"/{self.OPENAPI_SPEC_FILE}",
            "endpoint": self._generate_api_spec_fn(generator.api),
            "methods": ["GET"],
            "response_class": self.YAMLResponse,
            "operation_id": "OpenAPISpec",
            "description": "ChatGPT plugin spec"
        }

    def _generate_manifest_fn(self, generator: ToolApiGenerator) -> Callable:
        def generate_manifest() -> dict:
            return json.loads(
                J2(self.OPENAI_TEMPLATE_PATH).render(
                    name_for_human=generator.tool.manifest["name"],
                    name_for_model=generator.tool.manifest["name"],
                    description_for_human=generator.tool.manifest["description"],
                    description_for_model=generator.tool.manifest["description"],
                    api_url=f"/{self.OPENAPI_SPEC_FILE}",
                    logo_url=f"/{self.LOGO_FILE}",
                    contact_email=generator.tool.manifest["contact_email"],
                    legal_info_url=generator.tool.manifest["legal_info_url"]
                )
            )

        return generate_manifest

    def _generate_api_spec_fn(self, api: FastAPI) -> Callable:
        def generate_api_spec() -> str:
            return yaml.safe_dump(api.openapi())

        return generate_api_spec
