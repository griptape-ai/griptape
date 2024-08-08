from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.rules import Rule, Ruleset

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = PromptImageGenerationEngine(
    image_generation_driver=driver,
)

positive_ruleset = Ruleset(name="positive rules", rules=[Rule("artistic"), Rule("watercolor")])
negative_ruleset = Ruleset(name="negative rules", rules=[Rule("blurry"), Rule("photograph")])

engine.run(
    prompts=["A dog riding a skateboard"],
    rulesets=[positive_ruleset],
    negative_rulesets=[negative_ruleset],
)
