import pytest

from griptape.utils import anthropic_utils


class TestAnthropicUtils:
    @pytest.mark.parametrize(
        ("model", "expected"),
        [
            # Older families and versions predating the deprecation still accept sampling params.
            ("claude-3-haiku", True),
            ("claude-3-opus", True),
            ("claude-sonnet-4-5", True),
            ("claude-haiku-4-5", True),
            ("claude-opus-4-5", True),
            ("claude-opus-4-6", True),
            # A missing minor is treated as .0: dated pre-4.6 snapshots (family-major-date, e.g. Opus
            # 4.0) and the .0 alias must not have the date read as the minor.
            ("claude-opus-4-20250514", True),
            ("claude-opus-4-0", True),
            ("claude-opus-4-1-20250805", True),
            ("claude-sonnet-4-20250514", True),
            # Major-only releases omit the minor entirely; non-Opus families still accept the params.
            ("claude-sonnet-5", True),
            ("claude-fable-5", True),
            # Opus 4.7 and every later Opus release have the params deprecated.
            ("claude-opus-4-7", False),
            ("claude-opus-4-7-20251101", False),
            ("claude-opus-4-8", False),
            ("claude-opus-4-8-20260101", False),
            ("claude-opus-4-10", False),
            ("claude-opus-5-0", False),
            # A future major-only Opus id (no minor) is still covered without a code change.
            ("claude-opus-5", False),
            # Bedrock aliases, provider prefixes, inference-profile IDs, and ARNs embed the version.
            ("anthropic.claude-sonnet-4-5-20250929-v1:0", True),
            ("anthropic.claude-opus-4-20250514-v1:0", True),
            ("us.anthropic.claude-opus-4-20250514-v1:0", True),
            ("anthropic.claude-opus-4-7-20251101-v1:0", False),
            ("us.anthropic.claude-opus-4-8-20260101-v1:0", False),
            ("global.anthropic.claude-opus-4-8-20260101-v1:0", False),
            (
                "arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.anthropic.claude-opus-4-8-20260101-v1:0",
                False,
            ),
            # Identifiers without a parseable Claude version are treated as supporting the params.
            ("ai21.j2", True),
            ("anthropic.claude-3-haiku-20240307-v1:0", True),
            ("gpt-4.1", True),
            ("foo", True),
        ],
    )
    def test_supports_sampling_params(self, model, expected):
        assert anthropic_utils.supports_sampling_params(model) == expected
