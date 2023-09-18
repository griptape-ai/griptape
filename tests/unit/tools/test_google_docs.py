from griptape.tools import GoogleDocsClient
from unittest.mock import patch
from google.auth.exceptions import MalformedError


class TestGoogleDocsClient:

    def test_create_google_doc(self):
        value = {
            "file_name": "test_document"
        }
        assert "Error creating Google Doc" in GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).create_google_doc(file_name=value["file_name"]).value

    def test_append_text(self):
        params = {
            "values": {
                "document_id": "test_doc_id"
            }
        }
        text = "Appending this text"
        assert "Error appending text to Google Doc" in GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).append_text(params, text).value

    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_prepend_text(self, mock_auth):
        mock_auth.side_effect = MalformedError('Mocked Error')
        params = {
            "values": {
                "document_id": "test_doc_id"
            }
        }
        text = "Prepending this text"
        assert "Error prepending text to Google Doc" in GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).prepend_text(params, text).value

    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_upload_document(self, mock_auth):
        mock_auth.side_effect = MalformedError('Mocked Error')
        params = {
            "values": {
                "file_path": "/path/to/your/file.txt",
                "file_name": "uploaded_file.txt",
                "mime_type": "text/plain"
            }
        }
        assert "error uploading document to Google Docs" in GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).upload_document(params).value

    def test_download_document(self):
        file_path = "folder_name/document_name"
        assert "Error downloading Google Doc" in GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        ).download_document(file_path).value
