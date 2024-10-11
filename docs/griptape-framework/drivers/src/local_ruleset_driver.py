import json
import os
from pathlib import Path

from griptape.drivers import LocalRulesetDriver
from griptape.rules import Ruleset

ruleset_dir = "path/to/ruleset/dir"
ruleset_name = "my_local_ruleset.json"
ruleset_path = Path(os.path.join(ruleset_dir, ruleset_name))

os.makedirs(ruleset_dir, exist_ok=True)

ruleset_path.write_text(json.dumps({"rules": [{"value": "Always talk like a pirate."}]}))

ruleset = Ruleset(
    name=ruleset_name,
    ruleset_driver=LocalRulesetDriver(persist_dir=ruleset_dir),
)
