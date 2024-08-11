from griptape.drivers import GriptapeCloudObservabilityDriver
from griptape.observability import Observability
from griptape.structures import Agent

observability_driver = GriptapeCloudObservabilityDriver()

with Observability(observability_driver=observability_driver):
    # Important! Only code within this block is subject to observability
    agent = Agent()
    agent.run("Name the five greatest rappers of all time")
