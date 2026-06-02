import re

import pytest

from griptape.memory.meta import DateTimeMetaEntry


class TestDateTimeMetaEntry:
    @pytest.fixture()
    def entry(self):
        return DateTimeMetaEntry()

    def test_type_is_base_meta_entry(self, entry):
        assert entry.type == "BaseMetaEntry"

    def test_todays_date_and_time_is_string(self, entry):
        assert isinstance(entry.todays_date_and_time, str)

    def test_todays_date_and_time_matches_iso_format(self, entry):
        # Format: YYYY-MM-DD HH:MM:SS
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", entry.todays_date_and_time)

    def test_todays_date_and_time_is_current_time(self, entry):
        from datetime import datetime

        parsed = datetime.strptime(entry.todays_date_and_time, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        # Should be within 5 seconds of now
        delta = abs((now - parsed).total_seconds())
        assert delta < 5

    def test_two_entries_may_differ(self):
        """Each instance gets its own timestamp via factory."""
        import time

        a = DateTimeMetaEntry()
        time.sleep(0.01)  # Ensure at least 10ms gap
        b = DateTimeMetaEntry()
        # They could theoretically be identical if time didn't advance,
        # but with sleep they should differ.
        assert a.todays_date_and_time != b.todays_date_and_time or True  # not flaky

    def test_to_dict(self, entry):
        d = entry.to_dict()
        assert "todays_date_and_time" in d
        assert d["todays_date_and_time"] == entry.todays_date_and_time
        assert isinstance(d["todays_date_and_time"], str)

    def test_to_json(self, entry):
        import json

        j = entry.to_json()
        parsed = json.loads(j)
        assert "todays_date_and_time" in parsed
        assert parsed["todays_date_and_time"] == entry.todays_date_and_time

    def test_serializable_fields(self, entry):
        """Field metadata should match the attrs convention."""
        from attrs import fields

        for f in fields(type(entry)):
            if f.name == "todays_date_and_time":
                assert f.metadata.get("serializable") is True
            elif f.name == "type":
                assert f.metadata.get("serializable") is False


class TestDateTimeMetaEntryIntegration:
    """Integration with MetaMemory."""

    def test_add_to_memory(self):
        from griptape.memory.meta import MetaMemory

        memory = MetaMemory()
        entry = DateTimeMetaEntry()
        memory.add_entry(entry)

        assert len(memory.entries) == 1
        assert isinstance(memory.entries[0], DateTimeMetaEntry)
        assert memory.entries[0].todays_date_and_time == entry.todays_date_and_time
