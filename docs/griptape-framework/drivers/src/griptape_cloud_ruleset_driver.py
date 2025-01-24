from griptape.drivers.ruleset.griptape_cloud import GriptapeCloudRulesetDriver
from griptape.rules import Ruleset

rulset = Ruleset(
    name="my_griptape_cloud_ruleset_alias",
    ruleset_driver=GriptapeCloudRulesetDriver(),
)
