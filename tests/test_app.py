from datetime import datetime

import pytest
import pytz

import app

SCHEDULE_LINK = 'https://camph.net/schedule/'


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
        assert e.start == tz.localize(datetime(2015, 11, 2, 17, 0, 0))
        assert e.end == tz.localize(datetime(2015, 11, 2, 20, 0, 0))
        assert e.title == "Open"
        assert e.url == "https://example.com/"

        d = {
            "start": "2015-11-02T17:00:00+09:00",
            "end": "2015-11-02T20:00:00+09:00",
            "url": None,
            "title": "Open"
        }
        e = app.Event.from_json(d)
        assert e.start == tz.localize(datetime(2015, 11, 2, 17, 0, 0))
        assert e.end == tz.localize(datetime(2015, 11, 2, 20, 0, 0))
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
        assert message == f"""本日の CAMPHOR- HOUSE の開館時間は15:00〜19:00です。
みなさんのお越しをお待ちしています!!

その他の開館日はこちら
{SCHEDULE_LINK}"""

        e = app.Event(
            start=datetime(2020, 4, 12, 15, tzinfo=tz),
            end=datetime(2020, 4, 12, 19, tzinfo=tz),
            url=None,
            title="Online Open")
        message = e.generate_message(datetime(2020, 4, 12, 10, tzinfo=tz))
        assert message == f"""本日の CAMPHOR- HOUSE のオンライン開館時間は15:00〜19:00です。
詳しくはCAMPHOR-のSlackをご覧ください!!

その他の開館日はこちら
{SCHEDULE_LINK}"""

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

    def test_generate_week_message_with_open(self):
        tz = pytz.timezone("Asia/Tokyo")
        e0 = app.Event(
            start=datetime(2019, 4, 1, 17, tzinfo=tz),
            end=datetime(2019, 4, 1, 19, tzinfo=tz),
            url=None,
            title="Open")
        e1 = app.Event(
            start=datetime(2019, 4, 3, 17, tzinfo=tz),
            end=datetime(2019, 4, 3, 19, tzinfo=tz),
            url=None,
            title="Open")
        message = app.generate_week_message([e0, e1], tz)
        assert message == [f"""今週の開館日です！
04/01 (月) 17:00〜19:00
04/03 (水) 17:00〜19:00

みなさんのお越しをお待ちしています!!

その他の開館日はこちら
{SCHEDULE_LINK}"""]

    def test_generate_week_message_with_online_open(self):
        tz = pytz.timezone("Asia/Tokyo")
        e0 = app.Event(
            start=datetime(2020, 4, 1, 17, tzinfo=tz),
            end=datetime(2019, 4, 1, 19, tzinfo=tz),
            url=None,
            title="Online Open")
        e1 = app.Event(
            start=datetime(2020, 4, 3, 17, tzinfo=tz),
            end=datetime(2020, 4, 3, 19, tzinfo=tz),
            url=None,
            title="Online Open")
        message = app.generate_week_message([e0, e1], tz)
        assert message == [f"""今週のオンライン開館日です！
04/01 (水) 17:00〜19:00
04/03 (金) 17:00〜19:00

詳しくはCAMPHOR-のSlackをご覧ください!!

その他の開館日はこちら
{SCHEDULE_LINK}"""]

    def test_generate_week_message_with_event(self):
        tz = pytz.timezone("Asia/Tokyo")
        e0 = app.Event(
            start=datetime(2019, 4, 2, 17, tzinfo=tz),
            end=datetime(2019, 4, 2, 19, tzinfo=tz),
            url=None,
            title="Python Event")
        message = app.generate_week_message([e0], tz)
        assert message == ["""今週のイベント情報です！
Python Event 04/02 (火) 17:00〜19:00

お申し込みの上ご参加ください。
みなさんのお越しをお待ちしています!!"""]

    def test_generate_week_message_with_nothing(self):
        tz = pytz.timezone("Asia/Tokyo")
        message = app.generate_week_message([], tz)
        assert message == []

    def test_generate_week_message_with_event_and_open(self):
        tz = pytz.timezone("Asia/Tokyo")
        e0 = app.Event(
            start=datetime(2019, 4, 2, 17, tzinfo=tz),
            end=datetime(2019, 4, 2, 19, tzinfo=tz),
            url='https://example.com/',
            title="Python Event")
        e1 = app.Event(
            start=datetime(2019, 4, 1, 17, tzinfo=tz),
            end=datetime(2019, 4, 1, 19, tzinfo=tz),
            url=None,
            title="Open")
        e2 = app.Event(
            start=datetime(2019, 4, 3, 17, tzinfo=tz),
            end=datetime(2019, 4, 3, 19, tzinfo=tz),
            url=None,
            title="Open")

        message = app.generate_week_message([e0, e1, e2], tz)
        assert message == [f"""今週の開館日です！
04/01 (月) 17:00〜19:00
04/03 (水) 17:00〜19:00

みなさんのお越しをお待ちしています!!

その他の開館日はこちら
{SCHEDULE_LINK}""",
                           """今週のイベント情報です！
Python Event 04/02 (火) 17:00〜19:00
https://example.com/

お申し込みの上ご参加ください。
みなさんのお越しをお待ちしています!!"""]

    def test_generate_week_message_with_event_open_and_online_open(self):
        tz = pytz.timezone("Asia/Tokyo")
        e0 = app.Event(
            start=datetime(2019, 4, 2, 17, tzinfo=tz),
            end=datetime(2019, 4, 2, 19, tzinfo=tz),
            url='https://example.com/',
            title="Python Event")
        e1 = app.Event(
            start=datetime(2019, 4, 1, 17, tzinfo=tz),
            end=datetime(2019, 4, 1, 19, tzinfo=tz),
            url=None,
            title="Open")
        e2 = app.Event(
            start=datetime(2019, 4, 3, 17, tzinfo=tz),
            end=datetime(2019, 4, 3, 19, tzinfo=tz),
            url=None,
            title="Open")
        e3 = app.Event(
            start=datetime(2019, 4, 4, 17, tzinfo=tz),
            end=datetime(2019, 4, 4, 19, tzinfo=tz),
            url=None,
            title="Online Open")

        message = app.generate_week_message([e0, e1, e2, e3], tz)
        assert message == [f"""今週の開館日です！
04/01 (月) 17:00〜19:00
04/03 (水) 17:00〜19:00

みなさんのお越しをお待ちしています!!

その他の開館日はこちら
{SCHEDULE_LINK}""",
                           f"""今週のオンライン開館日です！
04/04 (木) 17:00〜19:00

詳しくはCAMPHOR-のSlackをご覧ください!!

その他の開館日はこちら
{SCHEDULE_LINK}""",
                           """今週のイベント情報です！
Python Event 04/02 (火) 17:00〜19:00
https://example.com/

お申し込みの上ご参加ください。
みなさんのお越しをお待ちしています!!"""]
