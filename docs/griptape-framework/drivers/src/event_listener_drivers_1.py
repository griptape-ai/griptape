import os

from griptape.drivers import AmazonSqsEventListenerDriver
from griptape.events import EventListener, event_bus
from griptape.rules import Rule
from griptape.structures import Agent

event_bus.add_event_listeners(
    [
        EventListener(
            driver=AmazonSqsEventListenerDriver(
                queue_url=os.environ["AMAZON_SQS_QUEUE_URL"],
            ),
        ),
    ]
)


agent = Agent(
    rules=[
        Rule(value="You will be provided with a block of text, and your task is to extract a list of keywords from it.")
    ],
)

agent.run(
    """Black-on-black ware is a 20th- and 21st-century pottery tradition developed by the Puebloan Native American ceramic artists in Northern New Mexico.
    Traditional reduction-fired blackware has been made for centuries by pueblo artists.
    Black-on-black ware of the past century is produced with a smooth surface, with the designs applied through selective burnishing or the application of refractory slip.
    Another style involves carving or incising designs and selectively polishing the raised areas.
    For generations several families from Kha'po Owingeh and P'ohwhóge Owingeh pueblos have been making black-on-black ware with the techniques passed down from matriarch potters. Artists from other pueblos have also produced black-on-black ware.
    Several contemporary artists have created works honoring the pottery of their ancestors."""
)
