import pytest
import os
from tests.utils.structure_runner import (
    run_structure,
    OUTPUT_RULESET,
    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
    prompt_driver_id_fn,
)


class TestGoogleDocsClient:
    @pytest.fixture(
        autouse=True,
        params=TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=prompt_driver_id_fn,
    )
    def agent(self, request):
        from griptape.structures import Agent
        from griptape.tools import GoogleDocsClient

        return Agent(
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
            memory=None,
            prompt_driver=request.param,
            rulesets=[OUTPUT_RULESET],
        )

    def test_create_google_doc(self, agent):
        result = run_structure(
            agent, 'Create a Google Doc called "Test Document".'
        )

        assert result["task_result"] == "success"
        assert result["task_output"] is not None

    def test_append_text(self, agent):
        result = run_structure(
            agent,
            'Append text "Appended Text." to the Google Doc "Test Document".',
        )

        assert result["task_result"] == "success"

    def test_prepend_text(self, agent):
        result = run_structure(
            agent,
            'Prepend text "Prepended Text." to the Google Doc "Test Document".',
        )

        assert result["task_result"] == "success"

    def test_download_google_doc(self, agent):
        result = run_structure(
            agent, 'Download the Google Doc "Test Document".'
        )

        assert result["task_result"] == "success"
        assert result["task_output"] is not None

    def test_save_content_to_google_doc(self, agent):
        result = run_structure(
            agent,
            'Save content "Hello, Google Doc!" to the Google Doc "Test Document".',
        )

        assert result["task_result"] == "success"
