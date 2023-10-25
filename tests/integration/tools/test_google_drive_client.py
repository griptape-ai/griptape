import pytest
import os
from tests.utils.structure_runner import (
    run_structure,
    OUTPUT_RULESET,
    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
    prompt_driver_id_fn,
)


class TestGoogleDriveClient:
    @pytest.fixture(
        autouse=True,
        params=TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=prompt_driver_id_fn,
    )
    def agent(self, request):
        from griptape.structures import Agent
        from griptape.tools import GoogleDriveClient

        return Agent(
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
            memory=None,
            rulesets=[OUTPUT_RULESET],
        )

    def test_list_files(self, agent):
        result = run_structure(agent, "List all files on Google Drive.")

        assert result["task_result"] == "success"
        assert result["task_output"] is not None

    def test_download_file(self, agent):
        result = run_structure(
            agent, 'Download the file called "sample1.txt" from Google Drive.'
        )

        assert result["task_result"] == "success"
        assert result["task_output"] is not None

    def test_save_content(self, agent):
        result = run_structure(
            agent,
            'Save content "Hello, Google Drive!" on Google Drive as "hello.txt".',
        )

        assert result["task_result"] == "success"

    def test_search_files_by_name(self, agent):
        result = run_structure(
            agent, 'Search files with name "hello.txt" on Google Drive.'
        )

        assert result["task_result"] == "success"
        assert result["task_output"] is not None

    def test_search_files_by_content(self, agent):
        result = run_structure(
            agent,
            'Search files with content "Hello, Google Drive!" on Google Drive.',
        )

        assert result["task_result"] == "success"
        assert result["task_output"] is not None
