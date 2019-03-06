#!/usr/bin/env python3

import argparse, feedparser, re

class Feed():
    def __init__(self, feed_id=None, url=None):
        self.url = url
        self.feed = self._fetch(self.url)
        self.entries = self.feed.get('entries', [])
        self.items = self._get_items()

    def _get_items(self):
        items = []
        for e in self.entries:
            items.append(FeedItem(e))
        return items

    def _fetch(self, url=None):
        if url is None:
            f = feedparser.parse(self.url)
        else:
            f = feedparser.parse(url)
        return f

class FeedItem():
    def __init__(self, entry):
        self.posted = False
        self.guid = entry.get('id')
        self.title = entry.get('title')
        self.link = entry.get('link')
        self.image = self._get_image(entry.get('media_content'))

    def _get_image(self, media_content):
        if isinstance(media_content, list) and len(media_content):
            full_url = media_content[0].get('url')
            m = re.match(
                '(https?:\/\/.*\/.*\.(jpg|png))',
                full_url,
                re.IGNORECASE
            )
            if m:
                return m.group(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--feed-id',
        help="An arbitrary identifier for this feed",
        required=True)
    parser.add_argument('--feed-url', help="The feed URL", required=True)
    parser.add_argument('--fetch-only',
        help="Don't publish to Diaspora, queue the new feed items for later",
        action='store_true',
        default=False
    )
    args = parser.parse_args()
    feed = Feed(url=args.feed_url)

    for e in feed.items:
        print()
        print(f'guid\t: {e.guid}')
        print(f'title\t: {e.title}')
        print(f'link\t: {e.link}')
        print(f'image\t: {e.image}')

main()
