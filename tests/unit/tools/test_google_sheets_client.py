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
        result = client.list_spreadsheets({"values": params})

        assert isinstance(result, ErrorArtifact)
        assert "error listing spreadsheet due to malformed credentials:" in result.value

    def test_create_spreadsheet(self, client):
        params = {"title": "Test Spreadsheet"}
        result = client.create_spreadsheet({"values": params})

        assert isinstance(result, ErrorArtifact)
        assert "error creating spreadsheet due to malformed credentials" in result.value

    def test_upload_spreadsheet(self, client):
        params = {
            "file_name": "test_sheet.xlsx",
            "file_path": "/path/to/your/test_sheet.xlsx",
            "file_type": "excel"
        }
        result = client.upload_spreadsheet({"values": params})

        assert isinstance(result, ErrorArtifact)
        assert "error uploading spreadsheet due to malformed credentials:" in result.value

    def test_modify_cell(self, client):
        params = {"file_path": "Test Spreadsheet", "range": "A1", "values": ["Hello"], "operation": "update"}
        result = client.modify_cell({"values": params})
    
        assert isinstance(result, ErrorArtifact)
        assert "error modifying value in cell due to malformed credentials:" in result.value


