import json
from typing import Optional
from warpspeed import utils
from warpspeed.tools import Tool
from attrs import define, field


@define
class AwsTool(Tool):
    policy: Optional[str] = field(default=None, kw_only=True)

    def run(self, command: str) -> str:
        result = utils.CommandRunner().run(f"AWS_PAGER='' {command} --output json")

        if result == "":
            return "[]"
        else:
            try:
                final_result = utils.minify_json(result)
            except Exception:
                final_result = result

            return final_result

    @property
    def schema_kwargs(self) -> dict:
        return {
            "policy": json.dumps(utils.minify_json(self.policy)).strip('"') if self.policy else None
        }
