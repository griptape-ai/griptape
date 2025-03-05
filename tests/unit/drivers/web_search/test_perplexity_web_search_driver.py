from unittest.mock import Mock

import pytest

from griptape.drivers.web_search.perplexity_web_search_driver import PerplexityWebSearchDriver


class TestPerplexityWebSearchDriver:
    @pytest.fixture(autouse=True)
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_function = Mock(arguments='{"foo": "bar"}', id="mock-id")
        mock_function.name = "MockTool_test"
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[
                Mock(
                    message=Mock(
                        content="The number of stars in the Milky Way galaxy is estimated to be between 100 billion and 400 billion stars. The most recent estimates from the Gaia mission suggest that there are approximately 100 to 400 billion stars in the Milky Way, with significant uncertainties remaining due to the difficulty in detecting faint red dwarfs and brown dwarfs.",
                        audio=None,
                        tool_calls=None,
                    )
                )
            ],
            citations=[
                "https://www.astronomy.com/science/astro-for-kids-how-many-stars-are-there-in-space/",
                "https://www.esa.int/Science_Exploration/Space_Science/Herschel/How_many_stars_are_there_in_the_Universe",
                "https://www.space.com/25959-how-many-stars-are-in-the-milky-way.html",
                "https://www.space.com/26078-how-many-stars-are-there.html",
                "https://en.wikipedia.org/wiki/Milky_Way",
            ],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_chat_create

    @pytest.fixture()
    def driver(self):
        return PerplexityWebSearchDriver(model="foo", api_key="bar")

    def test_search(self, driver):
        results = driver.search("test")
        assert len(results) == 1
        assert results[0].value.startswith("The number of stars in the Milky Way")
        assert len(results[0].meta["citations"]) == 5

    def test_api_key_validation(self):
        with pytest.raises(ValueError, match="api_key is required"):
            assert PerplexityWebSearchDriver().prompt_driver
