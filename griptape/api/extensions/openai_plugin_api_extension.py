import functools
import json
from griptape.api.extensions import BaseApiExtension
from attr import define
from starlette.responses import Response
from griptape.tools import BaseTool
from griptape.utils import J2


@define
class OpenAiPluginApiExtension(BaseApiExtension):
    class YAMLResponse(Response):
        media_type = "text/yaml"

    OPENAI_TEMPLATE_PATH = "tools/chat_gpt_plugin_manifest.json.j2"
    OPENAPI_SPEC_FILE = "openapi.yaml"

    def generate_manifest_route(self) -> BaseApiExtension.Route:
        return BaseApiExtension.Route(
            f"{self.path_prefix}{self.OPENAI_TEMPLATE_PATH}",
            functools.partial(self.generate_manifest, self.tool),
            methods=["GET"],
            description="ChatGPT plugin manifest"
        )

    def generate_spec_route(self) -> BaseApiExtension.Route:
        return self.Route(
            f"{self.path_prefix}{self.OPENAPI_SPEC_FILE}",
            functools.partial(self.generate_api_spec, app),
            methods=["GET"],
            response_class=self.YAMLResponse,
            description="OpenAPI plugin spec"
        )

    def generate_manifest(self, tool: BaseTool) -> dict:
        return json.loads(
            J2(self.OPENAI_TEMPLATE_PATH).render(
                name_for_human=tool.manifest["name"],
                name_for_model=tool.manifest["name"],
                description_for_human=tool.manifest["description"],
                description_for_model=tool.manifest["description"],
                api_url=f"{self.full_host_path}{self.OPENAPI_SPEC_FILE}",
                logo_url=f"{self.full_host_path}logo.png",
                contact_email=tool.manifest["contact_email"],
                legal_info_url=tool.manifest["legal_info_url"]
            )
        )