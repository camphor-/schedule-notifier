from datetime import datetime, timedelta, tzinfo
from operator import methodcaller
from typing import Dict, Iterable, List, Optional

import click
import dateutil.parser
from kawasemi import Kawasemi
import pytz
import requests

WEEKDAY_NAMES = ['月', '火', '水', '木', '金', '土', '日']


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

    def generate_message(self, now: datetime) -> Optional[str]:
        tz = now.tzinfo
        if tz is None:
            raise ValueError("'now' must be timezone aware datetime")
        start = self.start.astimezone(tz).time().strftime("%H:%M")
        end = self.end.astimezone(tz).time().strftime("%H:%M")

        if self.title.lower() == "open":
            return f"""本日の CAMPHOR- HOUSE の開館時間は{start}〜{end}です。
みなさんのお越しをお待ちしています!!"""
        elif self.title.lower() == "online open":
            return f"""本日の CAMPHOR- HOUSE のオンライン開館時間は{start}〜{end}です。
詳しくはCAMPHOR-のSlackをご覧ください!!"""
        elif self.title.strip() != "":
            message = f"""「{self.title}」を{start}〜{end}に開催します!
みなさんのお越しをお待ちしています!!"""
            if self.url is not None and self.url != "":
                message += f"\n{self.url}"
            return message
        else:
            return None

    def get_day_and_time(self, tz: tzinfo) -> str:
        date = self.start.astimezone(tz).date().strftime("%m/%d")
        day = get_japanese_weekday(self.start.astimezone(tz).weekday())
        start = self.start.astimezone(tz).time().strftime("%H:%M")
        end = self.end.astimezone(tz).time().strftime("%H:%M")
        return f"{date} ({day}) {start}〜{end}\n"

    def get_day_and_time_with_title(self, tz: tzinfo) -> str:
        return f"{self.title} {self.get_day_and_time(tz)}"


def get_japanese_weekday(day: int) -> str:
    return WEEKDAY_NAMES[day]


def generate_week_message(events: List[Event], tz: tzinfo) -> List[str]:
    open_events = list(filter(lambda e: e.title.lower() == "open", events))
    online_open_events = list(
        filter(
            lambda e: e.title.lower() == "online open",
            events))
    other_events = list(
        filter(lambda e: e.title.lower() != "open" and
               e.title.lower() != "online open", events))

    messages = []

    open_message = generate_open_event_message(open_events, tz)
    if open_message != "":
        messages.append(open_message)

    online_open_message = generate_online_open_event_message(
        online_open_events, tz)
    if online_open_message != "":
        messages.append(online_open_message)

    other_message = generate_other_event_message(other_events, tz)
    if other_message != "":
        messages.append(other_message)

    return messages


def generate_open_event_message(open_events: List[Event], tz: tzinfo) -> str:
    if len(open_events) == 0:
        return ""

    message = "今週の開館日です！\n"
    for open in open_events:
        message += open.get_day_and_time(tz)
    message += "\nみなさんのお越しをお待ちしています!!"
    return message


def generate_online_open_event_message(
        online_open_events: List[Event], tz: tzinfo) -> str:
    if len(online_open_events) == 0:
        return ""

    message = "今週のオンライン開館日です！\n"
    for online in online_open_events:
        message += online.get_day_and_time(tz)
    message += "\nみなさんのお越しをお待ちしています!!"
    return message


def generate_other_event_message(other_events: List[Event], tz: tzinfo) -> str:
    if len(other_events) == 0:
        return ""
    message = "今週のイベント情報です！\n"
    for event in other_events:
        message += event.get_day_and_time_with_title(tz)
        if event.url is not None:
            message += f"{event.url}\n"
    message += "\nお申し込みの上ご参加ください。"
    message += "\nみなさんのお越しをお待ちしています!!"
    return message


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
    messages = generate_messages(events, now, week)
    if dry_run:
        for i, message in enumerate(messages):
            print(f"#{i + 1}\n{message}")
        return
    if len(messages) > 0:
        kawasemi = Kawasemi({
            "CHANNELS": {
                "twitter": {
                    "_backend": "kawasemi.backends.twitter.TwitterChannel",
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "access_token": access_token,
                    "access_token_secret": access_token_secret,
                }
            }
        })

        for message in messages:
            kawasemi.send(message)


def download_events(url: str) -> Optional[List[Event]]:
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    return [Event.from_json(e) for e in response.json()]


def generate_messages(events: Iterable[Event], now: datetime,
                      week: bool) -> List[str]:
    tz = now.tzinfo
    if tz is None:
        raise ValueError("'now' must be timezone aware datetime")
    now = now.astimezone(tz)

    if week:
        delta = timedelta(days=7)
        events = filter(lambda e: e.start.astimezone(tz).date() >= now.date()
                        and e.start.astimezone(tz).date() < now.date() + delta,
                        events)
        messages = generate_week_message(list(events), tz)
    else:
        events = filter(lambda e: e.start.astimezone(tz).date() == now.date(),
                        events)
        messages = [m for m in map(methodcaller("generate_message", now),
                                   events)
                    if m is not None]

    return messages


if __name__ == "__main__":
    main()
