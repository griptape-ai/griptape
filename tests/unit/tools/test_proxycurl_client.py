from unittest.mock import patch
from griptape.artifacts import ErrorArtifact
from griptape.tools import ProxycurlClient


class TestProxycurlClient:
    @patch("griptape.tools.ProxycurlClient.get_profile")
    def test_get_profile(self, mock_get_profile):
        mock_get_profile.return_value = []

        profile_id = "any_username"
        client = ProxycurlClient(proxycurl_api_key="")
        params = {"values": {"profile_id": profile_id}}
        result = client.get_profile(params)

        assert isinstance(
            result, list
        ), "Expected list of TextArtifact instances"

    @patch("griptape.tools.ProxycurlClient.get_job")
    def test_get_job(self, mock_get_job):
        mock_get_job.return_value = []

        job_id = "123456"
        client = ProxycurlClient(proxycurl_api_key="")
        params = {"values": {"job_id": job_id}}
        result = client.get_job(params)

        assert isinstance(
            result, list
        ), "Expected list of TextArtifact instances"

    @patch("griptape.tools.ProxycurlClient.get_company")
    def test_get_company(self, mock_get_company):
        mock_get_company.return_value = []

        company_id = "any-company"
        client = ProxycurlClient(proxycurl_api_key="")
        params = {"values": {"company_id": company_id}}
        result = client.get_company(params)

        assert isinstance(
            result, list
        ), "Expected list of TextArtifact instances"

    @patch("griptape.tools.ProxycurlClient.get_school")
    def test_get_school(self, mock_get_school):
        mock_get_school.return_value = []

        school_id = "any-school"
        client = ProxycurlClient(proxycurl_api_key="")
        params = {"values": {"school_id": school_id}}
        result = client.get_school(params)

        assert isinstance(
            result, list
        ), "Expected list of TextArtifact instances"

    @patch("griptape.tools.ProxycurlClient.get_profile")
    def test_get_profile_with_invalid_api_key(self, mock_get_profile):
        mock_get_profile.return_value = ErrorArtifact("Some error message")

        api_key = "invalid_api_key"
        profile_id = "linkedin_profile_id_here"
        client = ProxycurlClient(proxycurl_api_key=api_key)
        params = {"values": {"profile_id": profile_id}}
        result = client.get_profile(params)

        assert isinstance(
            result, ErrorArtifact
        ), "Expected ErrorArtifact instance"
