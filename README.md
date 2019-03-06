# pod_feeder_v2

Publishes RSS/Atom feeds to Diaspora*

This is a lightweight, customizable "bot" script to harvest RSS/Atom feeds and
re-publish them to the Diaspora social network. It is posted here without
warranty, for public use.

v2 is a complete re-write of the
[original pod_feeder](https://github.com/rev138/pod_feeder) script which was
written (poorly) in perl and is no longer supported. Migrating to this version
is recommended.

## Installation
pod_feeder_v2 requires python3. You can easily install the dependencies with pip:

`pip3 install -r requirements.txt`

This script is intended to be run as a cron job, which might look something like this:

`@hourly ~/pod_feeder.py --feed-id myfeed --feed-url http://example.com/feeds/rss --pod-url https://diaspora.example.com --username user --password ******** --quiet`

There is also a database cleaner script that you can run as often as you like to
keep your database size under control:

`@weekly ~/clean_db.py feed.db > /dev/null 2>&1`

## Migrating from pod_feeder "classic"
1. pod_feeder_v2's database schema is backward-compatible with the original, so
you can point the script at your existing `feed.db` file (or whatever
yours is called).

2. The `--title-tags` and `--url-tags` arguments have not been carried forward
because in practice they generally create lots of spurious tags, and the
'stop words' feature is difficult to implement. `--user-agent` is not currently
implemented because the diaspy library does not support it.

3. Several new options, `--summary`, `--debug`, and `--quiet` have been added.

## Usage
```
usage: pod_feeder.py [-h] [--aspect-id ASPECT_ID] [--auto-tag AUTO_TAG]
                     [--category-tags] [--database DATABASE] [--embed-image]
                     --feed-id FEED_ID --feed-url FEED_URL
                     [--ignore-tag IGNORE_TAG] [--limit LIMIT] [--no-branding]
                     --pod-url POD_URL [--post-raw-link] [--timeout TIMEOUT]
                     [--username USERNAME] [--via VIA] [--summary | --body]
                     (--password PASSWORD | --fetch-only) [--debug | --quiet]

optional arguments:
  --aspect-id ASPECT_ID
                        Aspects to share with. May specified multiple times
                        (default: 'public')
  --auto-tag AUTO_TAG   Hashtags to add to all posts. May be specified
                        multiple times
  --category-tags       Attempt to automatically hashtagify RSS item
                        'categories'
  --database DATABASE   The SQLite file to store feed data (default:
                        'feed.db')
  --embed-image         Embed an image in the post if a link exists
  --feed-id FEED_ID     An arbitrary identifier for this feed
  --feed-url FEED_URL   The feed URL
  --ignore-tag IGNORE_TAG
                        Hashtags to filter out. May be specified multiple
                        times
  --limit LIMIT         Only post n items per script run, to prevent post-
                        spamming
  --no-branding         Do not include 'posted via pod_feeder_v2' footer to
                        posts
  --pod-url POD_URL     The pod URL
  --post-raw-link       Post the raw link instead of hyperlinking the article
                        title
  --timeout TIMEOUT     How many hours to keep attempting failed posts
                        (default 72)
  --username USERNAME   The D* login username
  --via VIA             Sets the 'posted via' text (default: 'pod_feeder_v2')
  --summary             Post the summary text of the feed item
  --body                Post the body (full text) of the feed item
  --password PASSWORD   The D* user password
  --fetch-only          Don't publish to Diaspora, queue the new feed items
                        for later
  --debug               Show debugging output
  --quiet               Suppress normal output
```

## A Note on YouTube Feeds

It is possible to publish a YouTube channel's feed, by using the following URL format:

    https://www.youtube.com/feeds/videos.xml?channel_id=<channel id>
