from datetime import datetime
from typing import Any, Iterable, List, Optional

from channels.backends.twitter import TwitterChannel
import click
import dateutil.parser
import pytz
import requests


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
    tz = pytz.timezone(timezone)
    now = datetime.now(tz=tz)

    _events = download_events(url, tz)
    if _events is None:
        return
    events = get_todays_events(_events, now)
    events = get_open_events(events)
    message = generate_message(events)
    if dry_run:
        print(message)
        return
    channel = TwitterChannel(api_key=api_key, api_secret=api_secret,
                             access_token=access_token,
                             access_token_secret=access_token_secret)
    channel.send(message)


def download_events(url: str, tz) -> Optional[List[Any]]:
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    events = response.json()
    for event in events:
        event["start"] = dateutil.parser.parse(event["start"]).astimezone(tz)
        event["end"] = dateutil.parser.parse(event["end"]).astimezone(tz)
    return events


def get_todays_events(events: Iterable[Any], now: datetime) -> Iterable[Any]:
    return filter(lambda e: e["start"].date() == now.date(), events)


def get_open_events(events: Iterable[Any]) -> Iterable[Any]:
    return filter(lambda e: e["title"] == "Open", events)


def generate_message(events: Iterable[Any]):
    events = list(events)
    if len(events) == 0:
        return "本日の CAMPHOR- HOUSE は閉館です。"
    else:
        event = events[0]
        start = event["start"].time().strftime("%H:%M")
        end = event["end"].time().strftime("%H:%M")
        return """本日の CAMPHOR- HOUSE の開館時間は{}〜{}です。
みなさんのお越しをお待ちしています!!""".format(start, end)


if __name__ == "__main__":
    main()
