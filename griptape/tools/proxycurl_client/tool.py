from __future__ import annotations
from griptape.artifacts import TextArtifact, ErrorArtifact, ListArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from schema import Schema, Literal
from attr import define, field
import requests
import logging


@define
class ProxycurlClient(BaseTool):
    ENDPOINTS = {
        "profile": "https://nubela.co/proxycurl/api/v2/linkedin",
        "job": "https://nubela.co/proxycurl/api/linkedin/job",
        "company": "https://nubela.co/proxycurl/api/linkedin/company",
        "school": "https://nubela.co/proxycurl/api/linkedin/school",
    }

    proxycurl_api_key: str = field(kw_only=True)
    timeout: int = field(default=10, kw_only=True)

    @activity(
        config={
            "description": "Can be used to get LinkedIn profile information from a person's profile",
            "schema": Schema({
                Literal(
                    "profile_id",
                    description="LinkedIn profile ID (i.e., https://www.linkedin.com/in/<profile_id>)"
                ): str
            }),
        }
    )
    def get_profile(self, params: dict) -> ListArtifact | ErrorArtifact:
        profile_id = params["values"].get("profile_id")

        return self._call_api("profile", "in", profile_id)

    @activity(
        config={
            "description": "Can be used to get LinkedIn job information from a job listing",
            "schema": Schema({
                Literal(
                    "job_id",
                    description="LinkedIn job ID (i.e., https://www.linkedin.com/jobs/view/<job_id>)"
                ): str
            }),
        }
    )
    def get_job(self, params: dict) -> ListArtifact | ErrorArtifact:
        job_id = params["values"].get("job_id")

        return self._call_api("job", "jobs/view", job_id)

    @activity(
        config={
            "description": "Can be used to get LinkedIn company information from a company's profile",
            "schema": Schema({
                Literal(
                    "company_id",
                    description="LinkedIn company ID (i.e., https://www.linkedin.com/company/<company_id>)"
                ): str
            }),
        }
    )
    def get_company(self, params: dict) -> ListArtifact | ErrorArtifact:
        company_id = params["values"].get("company_id")

        return self._call_api("company", "company", company_id)

    @activity(
        config={
            "description": "Can be used to get LinkedIn school information from a school's profile",
            "schema": Schema({
                Literal(
                    "school_id",
                    description="LinkedIn school ID (i.e., https://www.linkedin.com/school/<school_id>)"
                ): str
            }),
        }
    )
    def get_school(self, params: dict) -> ListArtifact | ErrorArtifact:
        school_id = params["values"].get("school_id")

        return self._call_api("school", "school", school_id)

    def _call_api(self, endpoint_name: str, path: str, item_id: str) -> ListArtifact | ErrorArtifact:
        headers = {"Authorization": f"Bearer {self.proxycurl_api_key}"}
        linkedin_url = "/".join(arg.strip("/") for arg in ["https://www.linkedin.com", path, item_id])
        params = {"url": linkedin_url}
        response = requests.get(
            self.ENDPOINTS[endpoint_name],
            params=params,
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            try:
                data = response.json()
                filtered_data = [
                    TextArtifact(f"{key}: {value}") for key, value in data.items() if value is not None and value
                ]

                return ListArtifact(
                    filtered_data
                )

            except ValueError:
                return ErrorArtifact("Failed to decode JSON from response")
        else:
            logging.error(f"Error retrieving information from LinkedIn. HTTP Status Code: {response.status_code}")

            return ErrorArtifact("Error retrieving information from LinkedIn")