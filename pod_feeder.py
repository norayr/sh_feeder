#!/usr/bin/env python3

import argparse, diaspy, feedparser, html2text, os.path, re, sqlite3, time

class Feed():
    """
    represents a parsed RSS/Atom feed
    """
    def __init__(self, feed_id=None, url=None, auto_tags=[],
        category_tags=False, ignore_tags=[]):
        self.auto_tags = auto_tags
        self.category_tags = category_tags
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
            item = FeedItem(e, category_tags=self.category_tags)
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
                    "INSERT INTO feeds(guid, feed_id, title, body, summary, \
                    link, image, image_title, hashtags, posted, timestamp) \
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        i.guid, self.feed_id, i.title, i.body, i.summary,
                        i.link, i.image, 'image', hashtags, '0', i.timestamp
                    )
                )
                conn.commit()

class FeedItem():
    """
    relevant fields extracted from a feed entry
    """
    def __init__(self, entry, category_tags=False):
        self.posted = False
        self.guid = entry.get('id')
        self.image = self.get_image(
            entry.get('media_content', []),
            entry.get('links', [])
        )
        self.title = entry.get('title')
        self.link = entry.get('link')
        self.timestamp = int(time.time())
        self.body = self.get_body(entry.get('content'))
        self.summary = self.get_summary(entry.get('summary_detail'))
        self.tags = []
        if category_tags:
            self.get_tags(entry.get('tags', []))

    def get_body(self, content):
        """
        convert the first item in the 'content' list
        """
        if content is not None:
            for c in content:
                return self.html2markdown(c).strip()
                break

    def get_image(self, media_content, links):
        """
        try to find a "cover" image for the entry
        """
        if isinstance(media_content, list) and len(media_content):
            for media in media_content:
                m = re.match(
                    '(https?:\/\/.*\/.*\.(gif|jpg|jpeg|png))',
                    media.get('url', ''),
                    re.IGNORECASE
                )
                if m:
                    return m.group(1)
        if isinstance(links, list) and len(links):
            for link in links:
                if re.match('image\/', link.get('type', '')):
                    return link.get('href')

    def get_summary(self, summary):
        """
        convert to markdown
        """
        if summary is not None:
            return self.html2markdown(summary).strip()

    def get_tags(self, tags):
        """
        returns a de-duped, sanitized list of tags from the entry
        """
        if tags is not None:
            for tag in tags:
                t = self.sanitize_tag(tag.get('term'))
                self.add_tags([t])

    def html2markdown(self, text_obj):
        """
        convert HTML to Markdown, or pass through plaintext
        """
        text = None
        if text_obj is not None:
            if text_obj.get('type') == 'text/html':
                text_maker = html2text.HTML2Text()
                text_maker.body_width = 0
                text = text_maker.handle(text_obj.get('value'))
            else:
                text = text_obj.get('value')
        return text

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

class PodClient():
    """
    handle interactions with the pod
    """
    def __init__(self, url=None, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.stream = self.connect()

    def connect(self):
        """
        login and return a Stream object
        """
        client = diaspy.connection.Connection(
            pod=self.url,
            username=self.username,
            password=self.password
        )
        client.login()
        # fetch=False to prevent diaspy from loading the stream needlessly
        return diaspy.streams.Stream(client, fetch=False)

    def post(self, message, aspect_ids=[], via=None):
        """
        post a message
        """
        if len(aspect_ids) == 0:
            aspect_ids.append('public')
        self.stream.post(
            text=message,
            aspect_ids=aspect_ids,
            provider_display_name=via
        )

    def format_post(self, content, body=False, embed_image=False,
        no_branding=False, post_raw_link=False, summary=False):
        """
        generate a post content string based on user inputs
        """
        output = ''
        title_string = '### %s\n\n%s' if post_raw_link else '### [%s](%s)'
        output = output + \
            title_string % (content['title'], content['link']) + '\n\n'
        if embed_image and content['image'] is not None:
            output = output + \
                '![%s](%s)\n\n' % (content['image_title'], content['image'])
        if summary and content['summary'] is not None:
            output = output + '%s\n\n' % content['summary']
        elif body and content['body'] is not None:
            output = output + '%s\n\n' % content['body']
        if len(content['hashtags']):
            output = output + content['hashtags'] + '\n'
        if not no_branding:
            output = output + \
            "posted by [pod_feeder_v2](https://gitlab.com/brianodonnell/pod_feeder_v2/)"
        return output

    def publish(self, content, args):
        """
        generate message text and post it to D*
        """
        message = self.format_post(content,
            body=args.body,
            embed_image=args.embed_image,
            post_raw_link=args.post_raw_link,
            summary=args.summary
        )
        self.post(message, via=args.via, aspect_ids=args.aspect_id)
        return True

def connect_db(file):
    """
    connect to the database and initialize if necessary
    """
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
            body VARCHAR(10240), summary VARCHAR(2048))'
        )
    else:
        # check to see if this is a v1 database schema
        summary_exists = False
        rows = conn.execute("PRAGMA table_info('feeds')").fetchall()
        for r in rows:
            if 'summary' in r:
                summary_exists = True
                break
        if summary_exists == False:
            # if the summary column doesn't exist, add it
            conn.execute("ALTER TABLE feeds ADD COLUMN summary VARCHAR(2048)")
    conn.row_factory = sqlite3.Row
    return conn

def publish_items(db, client, args=None):
    """
    find queued items in the database and publish them
    """
    query = "SELECT guid, title, link, image, image_title, hashtags, body, \
        summary FROM feeds WHERE feed_id == ? AND posted == 0 \
        AND timestamp > ? ORDER BY timestamp"
    if args.limit > 0:
        query = query + ' LIMIT %s' % args.limit
    timeout = int(time.time() - args.timeout * 3600)
    for row in db.execute(query, (args.feed_id, timeout)):
        if client.publish(row, args):
            db.execute(
                "UPDATE feeds SET posted = 1 WHERE guid = ?",
                (row['guid'],)
            )
            db.commit()

def parse_args():
    """
    proccess command line args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--aspect-id',
        help="Aspects to share with. \
            May specified multiple times (default: 'public')",
        action='append',
        default=[]
    )
    parser.add_argument('--auto-tag',
        help="Hashtags to add to all posts. May be specified multiple times",
        action='append',
        default=[]
    )
    parser.add_argument('--category-tags',
        help="Attempt to automatically hashtagify RSS item 'categories'",
        action='store_true',
        default=False
    )
    parser.add_argument('--database',
        help="The SQLite file to store feed data (default: 'feed.db')",
        default='feed.db'
    )
    parser.add_argument('--debug',
        help="Show debugging output",
        action='store_true',
        default=False
    )
    parser.add_argument('--embed-image',
        help="Embed an image in the post if a link exists",
        action='store_true',
        default=False
    )
    parser.add_argument('--feed-id',
        help="An arbitrary identifier for this feed",
        required=True)
    parser.add_argument('--feed-url', help="The feed URL", required=True)
    parser.add_argument('--ignore-tag',
        help="Hashtags to filter out. May be specified multiple times",
        action='append',
        default=[]
    )
    parser.add_argument('--limit',
        help='Only post n items per script run, to prevent post-spamming',
        type=int,
        default=-1
    )
    parser.add_argument('--no-branding',
        help="Do not include 'posted via pod_feeder_v2' footer to posts",
        action='store_true',
        default=False
    )
    parser.add_argument('--pod-url',
        help='The pod URL',
        required=True
    )
    parser.add_argument('--post-raw-link',
        help="Post the raw link instead of hyperlinking the article title",
        action='store_true',
        default=False
    )
    parser.add_argument('--timeout',
        help='How many hours to keep attempting failed posts (default 72)',
        type=int,
        default=72
    )
    parser.add_argument('--username',
        help='The D* login username',
        default='podmin'
    )
    parser.add_argument('--via',
        help="Sets the 'posted via' text (default: 'pod_feeder_v2')",
        default='pod_feeder_v2'
    )
    # allow full body or summary, not both
    post_content = parser.add_mutually_exclusive_group()
    post_content.add_argument('--summary',
        help="Post the summary text of the feed item",
        action='store_true',
        default=False
    )
    post_content.add_argument('--body',
        help="Post the body (full text) of the feed item",
        action='store_true',
        default=False
    )
    # we don't need/want a password when --fetch-only is used and vice versa
    fetch_only = parser.add_mutually_exclusive_group(required=True)
    fetch_only.add_argument('--password',
        help='The D* user password',
    )
    fetch_only.add_argument('--fetch-only',
        help="Don't publish to Diaspora, queue the new feed items for later",
        action='store_true',
        default=False
    )
    return parser.parse_args()

def main():
    args = parse_args()
    # slurp the feed
    feed = Feed(
        auto_tags=args.auto_tag,
        category_tags=args.category_tags,
        feed_id=args.feed_id,
        ignore_tags=args.ignore_tag,
        url=args.feed_url
    )
    # establish a database connection
    db = connect_db(args.database)
    # load the feed items into the database
    feed.load_db(db)
    # skip pusblishing if --fetch-only is used
    if not args.fetch_only:
        client = PodClient(
            url=args.pod_url,
            username=args.username,
            password=args.password
        )
        publish_items(db, client, args=args)
    db.close()

    if args.debug:
        for e in feed.items:
            print()
            print('guid\t: %s' % e.guid)
            print('title\t: %s' % e.title)
            print('link\t: %s' % e.link)
            print('image\t: %s' % e.image)
            print('tags\t: %s' % ", ".join(e.tags))
            print('time\t: %s' % e.timestamp)
            # print('body\t: %s' % e.body)
            # print('summary\t: %s' % e.summary)
            print()
            break
main()
