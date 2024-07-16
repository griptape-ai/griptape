import os

import pytest

from tests.utils.structure_tester import StructureTester


class TestGoogleDriveClient:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.structures import Agent
        from griptape.tools import GoogleDriveClient

        return StructureTester(
            Agent(
                tools=[
                    GoogleDriveClient(
                        service_account_credentials={
                            "type": os.environ["GOOGLE_ACCOUNT_TYPE"],
                            "project_id": os.environ["GOOGLE_PROJECT_ID"],
                            "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
                            "private_key": os.environ["GOOGLE_PRIVATE_KEY"],
                            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
                            "client_id": os.environ["GOOGLE_CLIENT_ID"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_x509_cert_url": os.environ["GOOGLE_CERT_URL"],
                        },
                        owner_email=os.environ["GOOGLE_OWNER_EMAIL"],
                    )
                ],
                prompt_driver=request.param,
                conversation_memory=None,
            )
        )

    def test_list_files(self, structure_tester):
        structure_tester.run("List all files on Google Drive.")

    def test_download_file(self, structure_tester):
        structure_tester.run('Download the file called "sample1.txt" from Google Drive.')

    def test_save_content(self, structure_tester):
        structure_tester.run('Save content "Hello, Google Drive!" on Google Drive as "hello.txt".')

    def test_search_files_by_name(self, structure_tester):
        structure_tester.run('Search files with name "hello.txt" on Google Drive.')

    def test_search_files_by_content(self, structure_tester):
        structure_tester.run('Search files with content "Hello, Google Drive!" on Google Drive.')
