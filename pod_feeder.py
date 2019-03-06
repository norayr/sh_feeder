#!/usr/bin/env python3

import argparse, feedparser

class Feed():
    def __init__(self, url):
        self.url = url
        self.feed = self._fetch(self.url)

    def _fetch(self, url=None):
        if url is None:
            f = feedparser.parse(self.url)
        else:
            f = feedparser.parse(url)
        return f

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--feed-url', help="The feed URL")
    parser.add_argument(
        '--fetch-only',
        help="Don't publish to Diaspora, \
            just queue the new feed items for later",
        action='store_true',
        default=False
    )
    args = parser.parse_args()

    feed = Feed(args.feed_url)
    print(feed.feed)

main()
