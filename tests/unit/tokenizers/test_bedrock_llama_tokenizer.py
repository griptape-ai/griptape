import pytest
from unittest import mock
from griptape.tokenizers import BedrockLlamaTokenizer


class TestBedrockLlamaTokenizer:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_tokenization = '{"generation_token_count": 13}'
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_tokenization
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_input_tokens_left(self):
        assert (
            BedrockLlamaTokenizer(model="meta.llama").count_input_tokens_left(
                "<s>[INST] <<SYS>>\n{{ system_prompt }}\n<</SYS>>\n\n{{ usr_msg_1 }} [/INST] {{ model_msg_1 }} </s><s>[INST] {{ usr_msg_2 }} [/INST]"
            )
            == 2026
        )

    def test_ouput_tokens_left(self):
        assert (
            BedrockLlamaTokenizer(model="meta.llama").count_output_tokens_left(
                "<s>[INST] <<SYS>>\n{{ system_prompt }}\n<</SYS>>\n\n{{ usr_msg_1 }} [/INST] {{ model_msg_1 }} </s><s>[INST] {{ usr_msg_2 }} [/INST]"
            )
            == 2026
        )
