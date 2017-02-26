from datetime import datetime
from operator import methodcaller
from typing import Dict, Iterable, List, Optional

from channels.backends.twitter import TwitterChannel
import click
import dateutil.parser
import pytz
import requests


class Event:
    # flake8 does not support variable annotations...
    # start: datetime
    # end: datetime
    # title: str
    # url: Optional[str]

    def __init__(self, *, start, end, title, url):
        self.start = start
        self.end = end
        self.title = title
        self.url = url

    @classmethod
    def from_json(cls, data: Dict[str, Optional[str]]) -> "Event":
        start = dateutil.parser.parse(data["start"])
        end = dateutil.parser.parse(data["end"])
        return cls(start=start, end=end, title=data["title"], url=data["url"])

    def generate_message(self, now: datetime) -> Optional[str]:
        tz = now.tzinfo
        if tz is None:
            raise ValueError("'now' must be timezone aware datetime")
        # TODO: Support other kinds of events
        if self.title.lower() == "open":
            start = self.start.astimezone(tz).time().strftime("%H:%M")
            end = self.end.astimezone(tz).time().strftime("%H:%M")
            return """本日の CAMPHOR- HOUSE の開館時間は{}〜{}です。
みなさんのお越しをお待ちしています!!""".format(start, end)
        else:
            return None


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
def main(url: str, api_key: str, api_secret: str, access_token: str,
         access_token_secret: str, dry_run: bool, timezone: str):
    now = datetime.now(tz=pytz.timezone(timezone))

    events = download_events(url)
    if events is None:
        return
    messages = generate_messages(events, now)
    if dry_run:
        for i, message in enumerate(messages):
            print("#{}\n{}".format(i + 1, message))
        return
    channel = TwitterChannel(api_key=api_key, api_secret=api_secret,
                             access_token=access_token,
                             access_token_secret=access_token_secret)
    for message in messages:
        channel.send(message)


def download_events(url: str) -> Optional[List[Event]]:
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    return [Event.from_json(e) for e in response.json()]


def generate_messages(events: Iterable[Event], now: datetime) -> List[str]:
    tz = now.tzinfo
    if tz is None:
        raise ValueError("'now' must be timezone aware datetime")
    now = now.astimezone(tz)
    events = filter(lambda e: e.start.astimezone(tz).date() == now.date(),
                    events)
    messages = [m for m in map(methodcaller("generate_message", now), events)
                if m is not None]

    if len(messages) == 0:
        messages.append("本日の CAMPHOR- HOUSE は閉館です。")

    return messages


if __name__ == "__main__":
    main()
