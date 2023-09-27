from griptape.tools import GoogleDocsClient
from unittest.mock import patch
from google.auth.exceptions import MalformedError
import pytest


class TestGoogleDocsClient:

    @pytest.fixture
    def mock_docs_client(self):
        return GoogleDocsClient(
            owner_email="tony@griptape.ai",
            service_account_credentials={}
        )

    def test_create_google_doc(self, mock_docs_client):
        file_name = "test_document"
        assert "Error creating Google Doc" in mock_docs_client.create_google_doc(file_name=file_name).value

    def test_append_text(self, mock_docs_client):
        file_path = "test_folder/test_document"
        text = "Appending this text"
        assert "Error appending text to Google Doc" in mock_docs_client.append_text_to_google_doc(file_path=file_path, text=text).value

    @patch('google.oauth2.service_account.Credentials.from_service_account_info')
    def test_prepend_text(self, mock_auth, mock_docs_client):
        mock_auth.side_effect = MalformedError('Mocked Error')
        file_path = "test_folder/test_document"
        text = "Prepending this text"
        assert "Error prepending text to Google Doc" in mock_docs_client.prepend_text_to_google_doc(file_path=file_path, text=text).value

    def test_download_google_docs(self, mock_docs_client):
        file_paths = ["folder_name/document_name"]
        assert "Error downloading Google Doc" in mock_docs_client.download_google_docs(file_paths=file_paths).value

    def test_save_content_to_google_doc(self, mock_docs_client):
        params = {"file_name": "test_document", "content": "Sample content"}
        expected_error_msg = "Error creating Google Doc"
        assert expected_error_msg in mock_docs_client.save_content_to_google_doc(params).value