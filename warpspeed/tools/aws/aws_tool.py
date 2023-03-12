from warpspeed import utils
from warpspeed.tools import Tool


class AwsTool(Tool):
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
