import pytest
from griptape.tools.youtube.tool import YouTubeTool
from griptape.artifacts import TextArtifact

# Test the search method of YouTubeTool
def test_search_youtube_videos():
    # Create an instance of the YouTubeTool
    tool = YouTubeTool()

    # Define a sample query
    query = "SpaceX Launch,3"  # Pass the query as a string

    # Call the search method with the query
    result = tool.search({"query": query})

    # Check if the result is a TextArtifact
    assert isinstance(result, TextArtifact)

    # Check if the length of the result is greater than 0
    assert len(result) > 0

if __name__ == '__main__':
    pytest.main()
