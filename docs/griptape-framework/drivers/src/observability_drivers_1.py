from griptape.drivers import GriptapeCloudObservabilityDriver
from griptape.observability import Observability
from griptape.rules import Rule
from griptape.structures import Agent

observability_driver = GriptapeCloudObservabilityDriver()

with Observability(observability_driver=observability_driver):
    agent = Agent(rules=[Rule("Output one word")])
    agent.run("Name an animal")
