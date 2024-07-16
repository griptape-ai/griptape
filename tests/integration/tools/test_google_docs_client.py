import os

import pytest

from tests.utils.structure_tester import StructureTester


class TestGoogleDocsClient:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.structures import Agent
        from griptape.tools import GoogleDocsClient

        return StructureTester(
            Agent(
                tools=[
                    GoogleDocsClient(
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
                conversation_memory=None,
                prompt_driver=request.param,
            )
        )

    def test_create_google_doc(self, structure_tester):
        structure_tester.run('Create a Google Doc called "Test Document".')

    def test_append_text(self, structure_tester):
        structure_tester.run('Append text "Appended Text." to the Google Doc "Test Document".')

    def test_prepend_text(self, structure_tester):
        structure_tester.run('Prepend text "Prepended Text." to the Google Doc "Test Document".')

    def test_download_google_doc(self, structure_tester):
        structure_tester.run('Download the Google Doc "Test Document".')

    def test_save_content_to_google_doc(self, structure_tester):
        structure_tester.run('Save content "Hello, Google Doc!" to the Google Doc "Test Document".')
