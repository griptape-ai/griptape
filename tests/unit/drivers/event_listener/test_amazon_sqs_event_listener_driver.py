import boto3
import pytest
from moto import mock_sqs

from griptape.drivers.event_listener.amazon_sqs_event_listener_driver import AmazonSqsEventListenerDriver
from tests.mocks.mock_event import MockEvent
from tests.utils.aws import mock_aws_credentials


class TestAmazonSqsEventListenerDriver:
    @pytest.fixture()
    def _run_before_and_after_tests(self):
        mock_aws_credentials()

    @pytest.fixture()
    def driver(self):
        mock = mock_sqs()
        mock.start()

        session = boto3.Session(region_name="us-east-1")
        response = session.client("sqs").create_queue(QueueName="foo-bar")
        queue_url = response["QueueUrl"]

        yield AmazonSqsEventListenerDriver(queue_url=queue_url, session=session)

        mock.stop()

    def test_init(self, driver):
        assert driver

    def test_try_publish_event_payload(self, driver):
        driver.try_publish_event_payload(MockEvent().to_dict())

    def test_try_publish_event_payload_batch(self, driver):
        driver.try_publish_event_payload_batch([MockEvent().to_dict() for _ in range(3)])
