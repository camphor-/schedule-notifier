from datetime import datetime

import pytest
import pytz

import app


class TestEvent:
    def test_from_json(self):
        tz = pytz.timezone("Asia/Tokyo")
        d = {
            "start": "2015-11-02T17:00:00+09:00",
            "end": "2015-11-02T20:00:00+09:00",
            "url": "https://example.com/",
            "title": "Open"
        }
        e = app.Event.from_json(d)
        assert e.start == datetime(2015, 11, 2, 17, 0, 0, tzinfo=tz)
        assert e.end == datetime(2015, 11, 2, 20, 0, 0, tzinfo=tz)
        assert e.title == "Open"
        assert e.url == "https://example.com/"

        d = {
            "start": "2015-11-02T17:00:00+09:00",
            "end": "2015-11-02T20:00:00+09:00",
            "url": None,
            "title": "Open"
        }
        e = app.Event.from_json(d)
        assert e.start == datetime(2015, 11, 2, 17, 0, 0, tzinfo=tz)
        assert e.end == datetime(2015, 11, 2, 20, 0, 0, tzinfo=tz)
        assert e.title == "Open"
        assert e.url is None

    def test_from_json_where_time_is_invalid(self):
        d = {
            "start": "ABCDEF",
            "end": "GHIJK",
            "url": None,
            "title": "Open"
        }
        with pytest.raises(ValueError):
            app.Event.from_json(d)

    def test_from_json_where_json_has_missing_key(self):
        d = {
            "title": "Open"
        }
        # TODO: we should raise more appropriate exception?
        with pytest.raises(KeyError):
            app.Event.from_json(d)

    def test_generate_message(self):
        tz = pytz.timezone("Asia/Tokyo")
        e = app.Event(
            start=datetime(2017, 3, 3, 15, tzinfo=tz),
            end=datetime(2017, 3, 3, 19, tzinfo=tz),
            url=None,
            title="Open")
        message = e.generate_message(datetime(2017, 3, 3, 10, tzinfo=tz))
        assert message == """本日の CAMPHOR- HOUSE の開館時間は15:00〜19:00です。
みなさんのお越しをお待ちしています!!"""

        e = app.Event(
            start=datetime(2017, 3, 3, 17, tzinfo=tz),
            end=datetime(2017, 3, 3, 19, tzinfo=tz),
            url="https://example.com/",
            title="Python Event")
        message = e.generate_message(datetime(2017, 3, 3, 10, tzinfo=tz))
        assert message == """「Python Event」を17:00〜19:00に開催します!
みなさんのお越しをお待ちしています!!
https://example.com/"""

        e = app.Event(
            start=datetime(2017, 3, 3, 17, tzinfo=tz),
            end=datetime(2017, 3, 3, 19, tzinfo=tz),
            url=None,
            title="Python Event")
        message = e.generate_message(datetime(2017, 3, 3, 10, tzinfo=tz))
        assert message == """「Python Event」を17:00〜19:00に開催します!
みなさんのお越しをお待ちしています!!"""

    def test_generate_message_where_title_is_missing(self):
        tz = pytz.timezone("Asia/Tokyo")
        e = app.Event(
            start=datetime(2017, 3, 3, 17, tzinfo=tz),
            end=datetime(2017, 3, 3, 19, tzinfo=tz),
            url=None,
            title="")
        message = e.generate_message(datetime(2017, 3, 3, 10, tzinfo=tz))
        assert message is None
