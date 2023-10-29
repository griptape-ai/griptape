import json
import pytest
from unittest.mock import patch
from griptape.artifacts import TextArtifact
from griptape.tools.openstreetmap.tool import OpenStreetMapTool


class TestOpenStreetMapTool:
    @pytest.fixture
    def tool(self):
        return OpenStreetMapTool()

    @patch.object(
        OpenStreetMapTool, "_search", return_value={"location": "test_location"}
    )
    def test_search(self, mock_search, tool):
        params = {"query": "test_location"}
        result = tool.search(params)

        assert isinstance(result, TextArtifact)
        assert result.value == json.dumps({"location": "test_location"})
        mock_search.assert_called_once_with("test_location")

    @patch.object(
        OpenStreetMapTool,
        "_search",
        side_effect=Exception(
            "An error occurred while searching for the location."
        ),
    )
    def test_search_exception(self, mock_search, tool):
        params = {"query": "test_location"}
        with pytest.raises(Exception) as e:
            tool.search(params)

        assert (
            str(e.value)
            == "An error occurred while searching for the location."
        )
