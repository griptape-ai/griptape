from griptape.drivers import GriptapeCloudRulesetDriver
from griptape.rules import Ruleset

rulset = Ruleset(
    name="my_griptape_cloud_ruleset_alias",
    ruleset_driver=GriptapeCloudRulesetDriver(),
)
