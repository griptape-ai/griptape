import functools
import json
from typing import Union
import yaml
from attr import define, field
from fastapi import FastAPI
from starlette.responses import Response

from griptape.artifacts import TextArtifact
from griptape.converters import BaseConverter
from griptape.core import BaseTool
from griptape.utils import J2


@define
class ChatgptPluginConverter(BaseConverter):
    class YAMLResponse(Response):
        media_type = "text/yaml"

    OPENAI_MANIFEST_FILE = "ai-plugin.json"
    OPENAPI_SPEC_FILE = "openapi.yaml"

    host: str = field(kw_only=True)
    path_prefix: str = field(default="/", kw_only=True)

    @property
    def full_host(self) -> str:
        return f"{self.host}{self.path_prefix}"

    def generate_manifest(self, tool: BaseTool) -> dict:
        return json.loads(
            J2(f"converters/chatgpt_plugin/{self.OPENAI_MANIFEST_FILE}.j2").render(
                name_for_human=tool.manifest["name"],
                name_for_model=tool.manifest["name"],
                description_for_human=tool.manifest["description"],
                description_for_model=tool.manifest["description"],
                api_url=f"{self.full_host}{self.OPENAPI_SPEC_FILE}",
                logo_url=f"{self.full_host}logo.png",
                contact_email=tool.manifest["contact_email"],
                legal_info_url=tool.manifest["legal_info_url"]
            )
        )

    def generate_api_spec(self, app: FastAPI) -> str:
        return yaml.safe_dump(app.openapi())

    def generate_api(self, tool: BaseTool) -> FastAPI:
        app = FastAPI()
        app.name = "app"

        app.add_api_route(
            f"{self.path_prefix}{self.OPENAI_MANIFEST_FILE}",
            functools.partial(self.generate_manifest, tool),
            methods=["GET"],
            description="ChatGPT plugin manifest"
        )

        app.add_api_route(
            f"{self.path_prefix}{self.OPENAPI_SPEC_FILE}",
            functools.partial(self.generate_api_spec, app),
            methods=["GET"],
            response_class=self.YAMLResponse,
            description="OpenAPI plugin spec"
        )

        for action in tool.activities():
            app.add_api_route(
                f"{self.path_prefix}{action.config['name']}",
                functools.partial(self.__execute_action, action),
                methods=["GET"],
                description=tool.full_activity_description(action)
            )

        return app

    def __execute_action(self, action: callable, value: str) -> Union[str, dict]:
        result = self.executor.execute(action, TextArtifact(value)).value

        try:
            return json.loads(result)
        except:
            return result
