from griptape.tools import GoogleDriveClient
from unittest.mock import patch
from google.auth.exceptions import MalformedError


class TestGoogleDriveClient:

    def test_list_files(self):
        value = {
            "max_files": 10
        }
        assert "error retrieving files from Drive" in GoogleDriveClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).list_files({"values": value}).value

    def test_upload_file(self):
        value = {
            "file_path": "/path/to/your/file.txt",
            "file_name": "uploaded_file.txt",
            "mime_type": "text/plain"
        }
        assert "error uploading file to Drive" in GoogleDriveClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).upload_file({"values": value}).value

    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_download_file(self, mock_auth):
        mock_auth.side_effect = MalformedError('Mocked Error')
        value = {
            "file_id": "example_file_id"
        }
        assert "error downloading file" in GoogleDriveClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).download_file({"values": value}).value

    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_search_file(self, mock_auth):
        mock_auth.side_effect = MalformedError('Mocked Error')
        value = {
            "file_name": "search_file_name.txt"
        }
        assert "error searching for file due to malformed credentials" in GoogleDriveClient(
            owner_email="tony@griptape.ai",  # Pass owner_email to the constructor
            service_account_credentials={}
        ).search_file({"values": value}).value
