from griptape.artifacts import ErrorArtifact
from griptape.tools import GoogleDriveClient


class TestGoogleDriveClient:
    def test_list_files(self):
        value = {"folder_path": "root"}  # This can be any folder path you want to test
        result = GoogleDriveClient(owner_email="tony@griptape.ai", service_account_credentials={}).list_files(
            {"values": value}
        )

        assert isinstance(result, ErrorArtifact)
        assert "error listing files due to malformed credentials" in result.value

    def test_save_content_to_drive(self):
        value = {"path": "/path/to/your/file.txt", "content": "Sample content for the file."}
        result = GoogleDriveClient(
            owner_email="tony@griptape.ai", service_account_credentials={}
        ).save_content_to_drive({"values": value})

        assert isinstance(result, ErrorArtifact)
        assert "error saving file to Google Drive" in result.value

    def test_download_files(self):
        value = {"file_paths": ["example_folder/example_file.txt"]}
        result = GoogleDriveClient(owner_email="tony@griptape.ai", service_account_credentials={}).download_files(
            {"values": value}
        )

        assert isinstance(result, ErrorArtifact)

        assert "error downloading file due to malformed credentials" in result.value

    def test_search_files(self):
        value = {"search_mode": "name", "file_name": "search_file_name.txt"}
        result = GoogleDriveClient(owner_email="tony@griptape.ai", service_account_credentials={}).search_files(
            {"values": value}
        )

        assert isinstance(result, ErrorArtifact)

        assert "error searching for file due to malformed credentials" in result.value

    def test_share_file(self):
        value = {"file_path": "/path/to/your/file.txt", "email_address": "sample_email@example.com", "role": "reader"}
        result = GoogleDriveClient(owner_email="tony@griptape.ai", service_account_credentials={}).share_file(
            {"values": value}
        )

        assert isinstance(result, ErrorArtifact)

        assert "error sharing file due to malformed credentials" in result.value
