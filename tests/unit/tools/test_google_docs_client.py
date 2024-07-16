import pytest


class TestGoogleDocsClient:
    @pytest.fixture()
    def mock_docs_client(self):
        from griptape.tools import GoogleDocsClient

        return GoogleDocsClient(owner_email="tony@griptape.ai", service_account_credentials={})

    def test_append_text(self, mock_docs_client):
        params = {"file_path": "test_folder/test_document", "text": "Appending this text"}
        result = mock_docs_client.append_text_to_google_doc({"values": params}).value
        assert "error appending text to Google Doc with path" in result

    def test_prepend_text(self, mock_docs_client):
        params = {"file_path": "test_folder/test_document", "text": "Prepending this text"}
        result = mock_docs_client.prepend_text_to_google_doc({"values": params}).value
        assert "error prepending text to Google Doc with path" in result

    def test_save_content_to_google_doc(self, mock_docs_client):
        params = {"file_path": "test_document", "content": "Sample content"}
        result = mock_docs_client.save_content_to_google_doc({"values": params}).value
        assert "Error creating/saving Google Doc:" in result
