from unittest import mock

import pytest
import requests


class TestGriptapeCloudFileManagerDriver:
    @pytest.fixture()
    def driver(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mocker.patch("requests.request", return_value=mock_response)

        return GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1")

    def test_instantiate_bucket_id(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mocker.patch("requests.request", return_value=mock_response)

        GriptapeCloudFileManagerDriver(base_url="https://api.griptape.ai", api_key="foo bar", bucket_id="1")

    def test_instantiate_no_bucket_id(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="GriptapeCloudFileManagerDriver requires an Bucket ID"):
            GriptapeCloudFileManagerDriver(api_key="foo bar")

    def test_instantiate_bucket_not_found(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=404)))

        with pytest.raises(ValueError, match="No Bucket found with ID: 1"):
            return GriptapeCloudFileManagerDriver(api_key="foo bar", bucket_id="1")

    def test_instantiate_bucket_500(self, mocker):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=500)))

        with pytest.raises(ValueError, match="Unexpected error when retrieving Bucket with ID: 1"):
            return GriptapeCloudFileManagerDriver(api_key="foo bar", bucket_id="1")

    def test_instantiate_no_api_key(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(ValueError, match="GriptapeCloudFileManagerDriver requires an API key"):
            GriptapeCloudFileManagerDriver(bucket_id="1")

    def test_instantiate_invalid_work_dir(self):
        from griptape.drivers import GriptapeCloudFileManagerDriver

        with pytest.raises(
            ValueError,
            match="GriptapeCloudFileManagerDriver requires 'workdir' to be an absolute path, starting with `/`",
        ):
            GriptapeCloudFileManagerDriver(api_key="foo bar", bucket_id="1", workdir="no_slash")

    def test_try_list_files(self, mocker, driver):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": [{"name": "foo/bar.pdf"}, {"name": "foo/baz.pdf"}]}
        mocker.patch("requests.request", return_value=mock_response)

        files = driver.try_list_files("foo/")

        assert len(files) == 2
        assert files[0] == "foo/bar.pdf"
        assert files[1] == "foo/baz.pdf"

    def test_try_list_files_postfix(self, mocker, driver):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": [{"name": "foo/bar.pdf"}, {"name": "foo/baz.pdf"}]}
        mocker.patch("requests.request", return_value=mock_response)

        files = driver.try_list_files("foo/", ".pdf")

        assert len(files) == 2
        assert files[0] == "foo/bar.pdf"
        assert files[1] == "foo/baz.pdf"

    def test_try_list_files_not_directory(self, mocker, driver):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": [{"name": "foo/bar"}, {"name": "foo/baz"}]}
        mocker.patch("requests.request", return_value=mock_response)

        with pytest.raises(NotADirectoryError):
            driver.try_list_files("foo")

    def test_try_load_file(self, mocker, driver):
        mock_url_response = mocker.Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {"url": "https://foo.bar"}
        mocker.patch("requests.request", return_value=mock_url_response)

        mock_file_response = mocker.Mock()
        mock_file_response.status_code = 200
        mock_file_response.content = b"bytes"
        mocker.patch("requests.get", return_value=mock_file_response)

        response = driver.try_load_file("foo")
        assert response == b"bytes"

    def test_try_load_file_directory(self, mocker, driver):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"url": "https://foo.bar"}
        mocker.patch("requests.request", return_value=mock_response)

        with pytest.raises(IsADirectoryError):
            driver.try_load_file("foo/")

    def test_try_load_file_asset_url_404(self, mocker, driver):
        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=404)))

        with pytest.raises(FileNotFoundError):
            driver.try_load_file("foo")

    def test_try_load_file_asset_url_500(self, mocker, driver):
        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=500)))

        with pytest.raises(requests.exceptions.HTTPError):
            driver.try_load_file("foo")

    def test_try_save_file(self, mocker, driver):
        mock_url_response = mocker.Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {"url": "https://foo.bar"}
        mocker.patch("requests.request", return_value=mock_url_response)

        mock_put_response = mocker.Mock()
        mock_put_response.status_code = 200
        mocker.patch("requests.put", return_value=mock_put_response)

        response = driver.try_save_file("foo", b"value")
        assert response == "buckets/1/assets/foo"

    def test_try_save_file_directory(self, mocker, driver):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"url": "https://foo.bar"}
        mocker.patch("requests.request", return_value=mock_response)

        with pytest.raises(IsADirectoryError):
            driver.try_save_file("foo/", b"value")

    def test_try_save_file_asset_url_404(self, mocker, driver):
        mock_create_response = mocker.Mock()
        mock_create_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock.Mock(status_code=404)
        )
        mocker.patch("requests.request", return_value=mock_create_response)

        with pytest.raises(requests.exceptions.HTTPError):
            driver.try_save_file("foo", b"value")

    def test_try_save_file_asset_url_500(self, mocker, driver):
        mocker.patch("requests.request", side_effect=requests.exceptions.HTTPError(response=mock.Mock(status_code=500)))

        with pytest.raises(requests.exceptions.HTTPError):
            driver.try_save_file("foo", b"value")
