# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from datetime import date
import json

from channels.backends.twitter import TwitterChannel
import click
import dateutil.parser
import requests


@click.command(help="CAMPHOR- Schedule Notifier")
@click.option("--config", type=click.Path(exists=True), default="config.json")
@click.option("--dry-run", "-n", default=False, is_flag=True,
              help="Write messages to stdout.")
def main(config, dry_run):
    with open(config) as f:
        config = json.load(f)
    events = download_events(config["url"])
    if events is None:
        return
    events = get_todays_events(events)
    events = get_open_events(events)
    message = generate_message(events)
    if dry_run:
        print(message)
        return
    channel = TwitterChannel(**config["twitter"])
    channel.send(message)


def download_events(url):
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        events = response.json()
        for event in events:
            event["start"] = dateutil.parser.parse(event["start"])
            event["end"] = dateutil.parser.parse(event["end"])
        return events


def get_todays_events(events):
    today = date.today()
    return filter(lambda e: e["start"].date() == today, events)


def get_open_events(events):
    return filter(lambda e: e["title"] == "Open", events)


def generate_message(events):
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
