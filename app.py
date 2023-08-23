from datetime import datetime, timedelta, tzinfo
from typing import Dict, List, Optional
from requests_oauthlib import OAuth1Session

import click
import dateutil.parser
import pytz
import requests
import textwrap

WEEKDAY_NAMES = ['月', '火', '水', '木', '金', '土', '日']

SCHEDULE_LINK = 'https://camph.net/schedule/'


class Event:
    start: datetime
    end: datetime
    title: str
    url: Optional[str]

    def __init__(self, *, start: datetime, end: datetime, title: str,
                 url: Optional[str]) -> None:
        self.start = start
        self.end = end
        self.title = title
        self.url = url

    @classmethod
    def from_json(cls, data: Dict[str, Optional[str]]) -> "Event":
        if data["start"] is not None:
            start = dateutil.parser.parse(data["start"])
        else:
            raise KeyError
        if data["end"] is not None:
            end = dateutil.parser.parse(data["end"])
        else:
            raise KeyError
        if data["title"] is not None:
            title = data["title"]
        else:
            raise KeyError
        return cls(start=start, end=end, title=title, url=data["url"])

    def get_start(self, tz: tzinfo) -> str:
        start = self.start.astimezone(tz).time().strftime("%H:%M")
        return start

    def get_end(self, tz: tzinfo) -> str:
        end = self.end.astimezone(tz).time().strftime("%H:%M")
        return end

    def get_day_and_time(self, tz: tzinfo) -> str:
        date = self.start.astimezone(tz).date().strftime("%m/%d")
        day = get_japanese_weekday(self.start.astimezone(tz).weekday())
        return f"{date} ({day}) {self.get_start(tz)}〜{self.get_end(tz)}"

    def get_day_and_time_with_title(self, tz: tzinfo) -> str:
        return f"{self.title} {self.get_day_and_time(tz)}"


class MessageGenerator:
    events: List[Event]
    now: datetime
    week: bool

    def __init__(self, *, events: List[Event], now: datetime,
                 week: bool) -> None:
        self.events = events
        if now.tzinfo is None:
            raise ValueError("'now' must be timezone aware datetime")
        self.tz = now.tzinfo
        self.now = now.astimezone(self.tz)
        self.week = week

    def generate_messages(self) -> List[str]:
        if self.week:
            delta = timedelta(days=7)
            events = list(filter(
                lambda e: e.start.astimezone(self.tz).date() >= self.now.date()
                and e.start.astimezone(self.tz).date() < self.now.date()
                + delta, self.events))
            messages = self.generate_week_messages(events)
        else:
            events = list(filter(
                lambda e: e.start.astimezone(self.tz).date()
                == self.now.date(), self.events))
            messages = self.generate_day_messages(events)
        return messages

    def generate_day_messages(self, events: List[Event]) -> List[str]:
        events_by_title = divide_events_by_title(events)
        messages: List[str] = []

        # 開館
        open_events = events_by_title["open"]
        if len(open_events) == 1:
            open_event = open_events[0]
            open_start = open_event.get_start(self.tz)
            open_end = open_event.get_end(self.tz)
            open_message = "本日の CAMPHOR- HOUSE の開館時間は"\
                f"{open_start}〜{open_end}です。\n"
            # CAMPHOR- Make あり
            make_events = events_by_title["make"]
            if len(make_events) == 1:
                make_event = make_events[0]
                make_start = make_event.get_start(self.tz)
                make_end = make_event.get_end(self.tz)
                # 時間同じ
                if open_start == make_start and open_end == make_end:
                    open_message += "CAMPHOR- Make も利用できます。\n"
                # 時間異なる
                else:
                    open_message += "CAMPHOR- Make は"\
                        f"{make_start}〜{make_end}に利用できます。\n"
            elif len(make_events) > 1:
                raise ValueError("The maximum number of Make events per day"
                                 " is one, but found several.")
            open_message += "みなさんのお越しをお待ちしています!!\n"
            open_message += "HOUSEの場所はこちら\nhttps://goo.gl/maps/qasTRtgjnoP2"
            messages.append(self.add_schedule_link(open_message))
        elif len(open_events) > 1:
            raise ValueError("The maximum number of Open events per day is"
                             " one, but found several.")

        # オンライン開館
        online_open_events = events_by_title["online open"]
        if len(online_open_events) == 1:
            online_open_event = online_open_events[0]
            start = online_open_event.get_start(self.tz)
            end = online_open_event.get_end(self.tz)
            online_open_message = textwrap.dedent(f"""\
                本日の CAMPHOR- HOUSE のオンライン開館時間は{start}〜{end}です。
                詳しくはCAMPHOR-のSlackをご覧ください!!
                """)
            messages.append(self.add_schedule_link(online_open_message))
        elif len(online_open_events) > 1:
            raise ValueError("The maximum number of Online Open events per"
                             " day is one, but found several.")

        # その他のイベント
        other_events = events_by_title["other"]
        if len(other_events) == 1:
            other_event = other_events[0]
            start = other_event.get_start(self.tz)
            end = other_event.get_end(self.tz)
            url = other_event.url
            other_message = textwrap.dedent(f"""\
                「{other_event.title}」を{start}〜{end}に開催します!
                みなさんのお越しをお待ちしています!!""")
            if url is not None and url != "":
                other_message += f"\n{url}"
            messages.append(other_message)
        elif len(other_events) > 1:
            raise ValueError("The maximum number of Other events per day"
                             " is one, but found several.")

        return messages

    def generate_week_messages(self, events: List[Event]) -> List[str]:
        events_by_title = divide_events_by_title(events)
        messages: List[str] = []

        # 開館日
        open_events = events_by_title["open"]
        if len(open_events) != 0:
            open_message = "今週の開館日です！\n"
            # CAMPHOR- Make が利用可能なとき、日時の後に`(Make)`を付ける
            for event in open_events:
                open_message += event.get_day_and_time(self.tz)
                if event.start.date() in [e.start.date()
                                          for e in events_by_title["make"]]:
                    open_message += " (Make)"
                open_message += "\n"
            open_message += "\nみなさんのお越しをお待ちしています!!\n"
            messages.append(self.add_schedule_link(open_message))

        # オンライン開館日
        online_open_events = events_by_title["online open"]
        if len(online_open_events) != 0:
            online_open_message = "今週のオンライン開館日です！\n"
            for event in online_open_events:
                online_open_message += event.get_day_and_time(self.tz) + "\n"
            online_open_message += "\n詳しくはCAMPHOR-のSlackをご覧ください!!\n"
            messages.append(self.add_schedule_link(online_open_message))

        # その他のイベント日
        other_events = events_by_title["other"]
        if len(other_events) != 0:
            other_message = "今週のイベント情報です！\n"
            for event in other_events:
                other_message += event.get_day_and_time_with_title(
                    self.tz) + "\n"
                if event.url is not None:
                    other_message += f"{event.url}\n"
            other_message += "\nお申し込みの上ご参加ください。\nみなさんのお越しをお待ちしています!!"
            messages.append(other_message)

        return messages

    def add_schedule_link(self, message: str) -> str:
        message += f"\nその他の開館日はこちら\n{SCHEDULE_LINK}"
        return message


def get_japanese_weekday(day: int) -> str:
    return WEEKDAY_NAMES[day]


def divide_events_by_title(events: List[Event]) -> Dict[str, List[Event]]:
    events_by_title: Dict[str, List[Event]] = {}
    for title in ["open", "make", "online open"]:
        events_by_title[title] = [
            e for e in events if e.title.lower() == title]
        events = [e for e in events if e.title.lower() != title]
    events_by_title["other"] = [e for e in events if e.title.strip() != ""]
    return events_by_title


def validate_datetime(ctx, param, value) -> Optional[datetime]:
    if value is None:
        return None
    try:
        dt = dateutil.parser.parse(value)
    except ValueError:
        ctx.fail(f"Failed to parse '{value}'")
    return dt  # WARNING: tzinfo might be None


@click.command(help="CAMPHOR- Schedule Notifier")
@click.option("--url", default="https://cal.camph.net/public/schedule.json",
              envvar="CSN_URL", help="URL of a schedule file.")
@click.option("--api-key", type=click.STRING,
              envvar="CSN_API_KEY", help="Twitter API Key.")
@click.option("--api-secret", type=click.STRING,
              envvar="CSN_API_SECRET", help="Twitter API Secret.")
@click.option("--access-token", type=click.STRING,
              envvar="CSN_ACCESS_TOKEN", help="Twitter Access Token.")
@click.option("--access-token-secret", type=click.STRING,
              envvar="CSN_ACCESS_TOKEN_SECRET",
              help="Twitter Access Token Secret.")
@click.option("--dry-run", "-n", default=False, is_flag=True,
              help="Write messages to stdout.")
@click.option("--timezone", default="Asia/Tokyo",
              help="Time zone used to show time. (default: Asia/Tokyo)")
@click.option("--now", callback=validate_datetime,
              help="Specify current time for debugging. (example: 2017-01-01)")
@click.option("--week", default=False, is_flag=True,
              envvar="CSN_WEEK", help="Notify weekly schedule.")
def main(url: str, api_key: str, api_secret: str, access_token: str,
         access_token_secret: str, dry_run: bool, timezone: str,
         now: datetime, week: bool) -> None:
    tz = pytz.timezone(timezone)
    if now is None:
        now = datetime.now(tz=tz)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=tz)

    events = download_events(url)
    if events is None:
        return
    mg = MessageGenerator(events=events, now=now, week=week)
    messages = mg.generate_messages()
    if dry_run:
        for i, message in enumerate(messages):
            print(f"#{i + 1}\n{message}")
        return
    if len(messages) > 0:
        twitter_client = OAuth1Session(api_key, api_secret, access_token, access_token_secret)
        endpoint = "https://api.twitter.com/2/tweets"
        
        for message in messages:
            twitter_client.post(endpoint, json={"text": message})



def download_events(url: str) -> Optional[List[Event]]:
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    return [Event.from_json(e) for e in response.json()]


if __name__ == "__main__":
    main()
