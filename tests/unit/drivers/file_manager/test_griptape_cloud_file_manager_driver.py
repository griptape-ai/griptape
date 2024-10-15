from unittest import mock

import pytest
import requests


class TestGriptapeCloudFileManagerDriver:
    def test_instantiate_bucket_id(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mocker.patch("requests.request", return_value=mock_response)

        GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1")

    def test_instantiate_bucket_name(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"bucket_id": "2"}
        mocker.patch("requests.request", return_value=mock_response)

        GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_name="foo")

    def test_instantiate_no_bucket_id_or_name(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="Either 'bucket_id' or 'bucket_name' must be provided."):
            GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar")

    def test_instantiate_both_bucket_id_or_name(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="Only one of 'bucket_id' or 'bucket_name' may be provided, not both."):
            GriptapeCloudFileManagerDriver(
                base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1", bucket_name="foo"
            )

    def test_instantiate_bucket_not_found(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=404)))

        with pytest.raises(ValueError, match="No Bucket found with ID: 1"):
            return GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1")

    def test_instantiate_bucket_500(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=500)))

        with pytest.raises(ValueError, match="Unexpected error when retrieving Bucket with ID: 1"):
            return GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1")

    def test_instantiate_no_api_key(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="GriptapeCloudFileManagerDriver requires an API key"):
            GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", bucket_id="1")

    def test_instantiate_invalid_work_dir(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="GriptapeCloudFileManagerDriver requires Workdir to be an absolute path"):
            GriptapeCloudFileManagerDriver(
                base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1", workdir="no_slash"
            )
