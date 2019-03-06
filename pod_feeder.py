#!/usr/bin/env python3

import argparse, feedparser, html2text, re, time

class Feed():
    """
    represents a parsed RSS/Atom feed
    """
    def __init__(self, feed_id=None, url=None):
        self.url = url
        self.feed = self.fetch(self.url)
        self.entries = self.feed.get('entries', [])
        self.items = self.get_items()

    def get_items(self):
        """
        returns a list of FeedItems
        """
        items = []
        for e in self.entries:
            items.append(FeedItem(e))
        return items

    def fetch(self, url=None):
        """
        returns a parsed feed from feedparser
        """
        if url is None:
            f = feedparser.parse(self.url)
        else:
            f = feedparser.parse(url)
        return f

class FeedItem():
    """
    relevant fields extracted from a feed entry
    """
    def __init__(self, entry):
        self.posted = False
        self.guid = entry.get('id')
        self.title = entry.get('title')
        self.link = entry.get('link')
        self.image = self.get_image(entry.get('media_content', []))
        self.timestamp = int(time.mktime(entry.get('published_parsed')))
        self.body = self.get_body(entry.get('content'))
        self.summary = self.get_summary(entry.get('summary_detail'))
        self.tags = []
        self.get_tags(entry.get('tags', []))

    def get_body(self, content):
        """
        convert the first item in the 'content' list
        """
        for c in content:
            return self.html2markdown(c)
            break

    def html2markdown(self, text_obj):
        """
        Convert HTML to Markdown, or pass through plaintext
        """
        text = None
        if text_obj.get('type') == 'text/html':
            text = html2text.html2text(text_obj.get('value'))
        else:
            text = text_obj.get('value')
        return text

    def get_image(self, media_content):
        """
        try to find a "cover" image for the entry
        """
        if isinstance(media_content, list) and len(media_content):
            full_url = media_content[0].get('url')
            m = re.match(
                '(https?:\/\/.*\/.*\.(jpg|png))',
                full_url,
                re.IGNORECASE
            )
            if m:
                return m.group(1)

    def get_summary(self, summary):
        """
        convert to markdown
        """
        return self.html2markdown(summary)

    def get_tags(self, tags):
        """
        returns a de-duped, sanitized list of tags from the entry
        """
        for tag in tags:
            t = self.sanitize_tag(tag.get('term'))
            if t == 'uncategorized':
                pass
            else:
                self.add_tags([t])

    def sanitize_tag(self, tag):
        return tag.lower().replace(' ', '').replace('#', '')

    def add_tags(self, tags):
        for tag in tags:
            t = self.sanitize_tag(tag)
            if len(t) and t not in self.tags:
                self.tags.append(t)


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
        print(f'tags\t: {", ".join(e.tags)}')
        print(f'time\t: {e.timestamp}')
        # print(f'body\t: {e.body}')
        # print(f'summary\t: {e.summary}')
        print()
        # break
main()
