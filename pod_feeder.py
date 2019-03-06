#!/usr/bin/env python3

import argparse, feedparser, html2text, os.path, re, sqlite3, time

class Feed():
    """
    represents a parsed RSS/Atom feed
    """
    def __init__(self, feed_id=None, url=None, auto_tags=[], ignore_tags=[]):
        self.auto_tags = auto_tags
        self.ignore_tags = ignore_tags
        self.feed_id = feed_id
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
            item = FeedItem(e)
            item.add_tags(self.auto_tags)
            item.remove_tags(self.ignore_tags)
            items.append(item)
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

    def load_db(self, conn):
        """
        updates feeds table with new items
        """
        for i in self.items:
            # check to see if the item is already in the db
            row = conn.execute(
                "SELECT guid FROM feeds WHERE guid = ?", (i.guid,)
            ).fetchone()
            if row is None:
                hashtags = ' '.join(i.tags)
                # if not, insert it
                conn.execute(
                    "INSERT INTO feeds(guid, feed_id, title, body, link, \
                    image, image_title, hashtags, posted, timestamp) \
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        i.guid, self.feed_id, i.title, i.body, i.link, i.image,
                        'image', hashtags, '0', i.timestamp
                    )
                )
                conn.commit()

class FeedItem():
    """
    relevant fields extracted from a feed entry
    """
    def __init__(self, entry):
        self.posted = False
        self.guid = entry.get('id')
        self.image = self.get_image(
            entry.get('media_content', []),
            entry.get('links', [])
        )
        self.title = entry.get('title')
        self.link = entry.get('link')
        self.timestamp = int(
            time.mktime(
                entry.get('published_parsed', time.gmtime())
            )
        )
        self.body = self.get_body(entry.get('content'))
        self.summary = self.get_summary(entry.get('summary_detail'))
        self.tags = []
        self.get_tags(entry.get('tags', []))

    def get_body(self, content):
        """
        convert the first item in the 'content' list
        """
        if content is not None:
            for c in content:
                return self.html2markdown(c)
                break

    def html2markdown(self, text_obj):
        """
        convert HTML to Markdown, or pass through plaintext
        """
        text = None
        if text_obj is not None:
            if text_obj.get('type') == 'text/html':
                text = html2text.html2text(text_obj.get('value'))
            else:
                text = text_obj.get('value')
        return text

    def get_image(self, media_content, links):
        """
        try to find a "cover" image for the entry
        """
        if isinstance(media_content, list) and len(media_content):
            for m in media_content:
                m = re.match(
                    '(https?:\/\/.*\/.*\.(jpg|png))',
                    m.get('url', ''),
                    re.IGNORECASE
                )
                if m:
                    return m.group(1)
        if isinstance(links, list) and len(links):
            for l in links:
                if re.match('image\/', l.get('type', '')):
                    return l.get('href')

    def get_summary(self, summary):
        """
        convert to markdown
        """
        if summary is not None:
            return self.html2markdown(summary)

    def get_tags(self, tags):
        """
        returns a de-duped, sanitized list of tags from the entry
        """
        if tags is not None:
            for tag in tags:
                t = self.sanitize_tag(tag.get('term'))
                self.add_tags([t])

    def sanitize_tag(self, tag):
        """
        remove spaces, lowercase, and add a '#'
        """
        return '#' + tag.lower().replace(' ', '').replace('#', '')

    def add_tags(self, tags):
        """
        add a list of tags to self.tags
        """
        for tag in tags:
            t = self.sanitize_tag(tag)
            if len(t) and t not in self.tags:
                self.tags.append(t)

    def remove_tags(self, tags):
        """
        remove a list of tags from self.tags
        """
        for tag in tags:
            t = self.sanitize_tag(tag)
            if t in self.tags:
                self.tags.remove(t)

def connect_db(file):
    # check to see if a new database needs to be initialized
    init_db = False if os.path.isfile(file) else True
    conn = sqlite3.connect(file)
    if init_db:
        # create the feeds table
        conn.execute(
            'CREATE TABLE feeds(guid VARCHAR(255) PRIMARY KEY, \
            feed_id VARCHAR(127), title VARCHAR(255), link VARCHAR(255), \
            image VARCHAR(255), image_title VARCHAR(255), \
            hashtags VARCHAR(255), timestamp INTEGER(10), posted INTEGER(1), \
            body VARCHAR(10000))'
        )
    return conn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto-tag',
        help="Hashtags to add to all posts. May be specified multiple times",
        action='append',
        default=[]
    )
    parser.add_argument('--database',
        help="The SQLite file to store feed data (default: 'feed.db')",
        default='feed.db'
    )
    parser.add_argument('--feed-id',
        help="An arbitrary identifier for this feed",
        required=True)
    parser.add_argument('--feed-url', help="The feed URL", required=True)
    parser.add_argument('--fetch-only',
        help="Don't publish to Diaspora, queue the new feed items for later",
        action='store_true',
        default=False
    )
    parser.add_argument('--ignore-tag',
        help="Hashtags to filter out. May be specified multiple times",
        action='append',
        default=[]
    )
    args = parser.parse_args()
    feed = Feed(
        auto_tags=args.auto_tag,
        feed_id=args.feed_id,
        ignore_tags=args.ignore_tag,
        url=args.feed_url
    )
    db = connect_db(args.database)

    feed.load_db(db)
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
        break
main()
