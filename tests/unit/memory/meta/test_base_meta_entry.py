from tests.mocks.mock_meta_entry import MockMetaEntry


class TestBaseMetaEntry:
    def test_to_json(self):
        assert MockMetaEntry().to_json() == '{"foo": "bar"}'
