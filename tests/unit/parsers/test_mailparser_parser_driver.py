from __future__ import annotations

import pytest

from griptape.drivers.parser.mailparser_parser_driver import MailparserParserDriver


class TestMailparserParserDriver:
    @pytest.fixture()
    def driver(self):
        return MailparserParserDriver()

    @pytest.fixture(params=["bytes_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_parse(self, driver, create_source):
        source = create_source("mail.txt").read()

        artifact = driver.parse([source])

        assert artifact.value[0].value.startswith("Hi Jane,")
