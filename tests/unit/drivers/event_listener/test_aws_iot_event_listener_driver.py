from pytest import fixture
from moto import mock_iotdata
import boto3
from tests.mocks.mock_event import MockEvent
from griptape.drivers.event_listener.aws_iot_core_event_listener_driver import AwsIotCoreEventListenerDriver
from tests.utils.aws import mock_aws_credentials


@mock_iotdata
class TestAwsIotCoreEventListenerDriver:
    @fixture(autouse=True)
    def run_before_and_after_tests(self):
        mock_aws_credentials()

    @fixture()
    def driver(self):
        return AwsIotCoreEventListenerDriver(
            iot_endpoint="foo bar", topic="fizz buzz", session=boto3.Session(region_name="us-east-1")
        )

    def test_init(self, driver):
        assert driver

    def test_try_publish_event_payload(self, driver):
        driver.try_publish_event_payload(MockEvent().to_dict())

    def test_try_publish_event_payload_batch(self, driver):
        driver.try_publish_event_payload_batch([MockEvent().to_dict() for _ in range(3)])
