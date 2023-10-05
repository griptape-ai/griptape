from griptape.tools import GoogleSheetsClient
from griptape.artifacts import ErrorArtifact, ListArtifact, InfoArtifact
import pytest


class TestGoogleSheetsClient:
    @pytest.fixture
    def client(self):
        return GoogleSheetsClient(owner_email="tony@griptape.ai", service_account_credentials={})

    def test_list_spreadsheets(self, client):
        params = {
            "folder_path": "root"
        }
        result = client.list_spreadsheets(params)

        assert isinstance(result, ErrorArtifact)
        assert "error listing spreadsheet due to malformed credentials:" in result.value

    def test_create_spreadsheet(self, client):
        params = {"title": "Test Spreadsheet"}
        result = client.create_spreadsheet(params)

        assert isinstance(result, ErrorArtifact)
        assert "error creating spreadsheet due to malformed credentials" in result.value

    def test_download_spreadsheets(self, client):
        params = {
            "file_paths": ["example_folder/example_file"],
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        result = client.download_spreadsheets(params)

        assert isinstance(result, ErrorArtifact)
        assert "error downloading spreadsheet due to malformed credentials" in result.value

    def test_upload_spreadsheet(self, client):
        params = {
            "file_name": "test_sheet.xlsx",
            "file_path": "/path/to/your/test_sheet.xlsx",
            "file_type": "excel"
        }
        result = client.upload_spreadsheet(params)

        assert isinstance(result, ErrorArtifact)
        assert "error uploading spreadsheet due to malformed credentials:" in result.value

    def test_share_spreadsheet(self, client):
        params = {
            "file_path": "example_folder/example_file",
            "email_address": "example@example.com",
            "role": "reader"
        }
        result = client.share_spreadsheet(params)

        assert isinstance(result, ErrorArtifact)
        assert "error sharing spreadsheet due to malformed credentials:" in result.value

    def test_check_permissions_for_spreadsheet(self, client):
        params = {"file_path": "example_folder/example_file"}
        result = client.list_permissions_for_spreadsheet(params)

        assert isinstance(result, ErrorArtifact)
        assert "error checking permissions due to malformed credentials:" in result.value

