import sqlite3, time, unittest
from unittest import mock
from pod_feeder_v2.pod_feeder import *


class TestFeed(unittest.TestCase):
    @mock.patch.object(Feed, "get_items")
    @mock.patch.object(Feed, "fetch")
    def test___init__(self, mock_fetch, mock_get_items):
        mock_fetch.return_value = {"entries": ["entry"]}
        mock_get_items.return_value = ["item"]
        # check defaults
        default = Feed()
        self.assertIsNone(default.feed_id)
        self.assertIsNone(default.url)
        self.assertEqual(default.auto_tags, [])
        self.assertFalse(default.category_tags)
        self.assertEqual(default.ignore_tags, [])
        self.assertFalse(default.debug)
        # verify custom values
        custom = Feed(
            feed_id="test",
            url="https://example.com",
            auto_tags=["auto"],
            category_tags=True,
            ignore_tags=["ignore"],
            debug=True,
        )
        self.assertEqual(custom.feed_id, "test")
        self.assertEqual(custom.url, "https://example.com")
        self.assertEqual(custom.auto_tags, ["auto"])
        self.assertTrue(custom.category_tags)
        self.assertEqual(custom.ignore_tags, ["ignore"])
        self.assertTrue(custom.debug)
        self.assertEqual(custom.feed, {"entries": ["entry"]})
        self.assertEqual(custom.entries, ["entry"])
        self.assertEqual(custom.items, ["item"])
        mock_fetch.assert_called_with("https://example.com")

    @mock.patch.object(FeedItem, "remove_tags")
    @mock.patch.object(FeedItem, "add_tags")
    @mock.patch.object(FeedItem, "__init__")
    def test_get_items(self, mock_init, mock_add_tags, mock_remove_tags):
        mock_init.return_value = None
        feed = Feed(
            auto_tags=["auto"], ignore_tags=["ignore"], url="https://example.com"
        )
        feed.entries = ["entry"]
        items = feed.get_items()
        self.assertIsInstance(items, list)
        for i in items:
            self.assertIsInstance(i, FeedItem)
        mock_init.assert_called_with("entry", category_tags=False)
        mock_add_tags.assert_called_with(["auto"])
        mock_remove_tags.assert_called_with(["ignore"])

    @mock.patch.object(feedparser, "parse")
    def test_fetch(self, mock_parse):
        mock_parse.return_value = {}
        default = Feed.__new__(Feed)
        default.url = "https://example.com"
        default.fetch()
        mock_parse.assert_called_with("https://example.com")
        with_url = Feed.__new__(Feed)
        with_url.url = "https://example.com"
        default.fetch("https://custom.example.com")
        mock_parse.assert_called_with("https://custom.example.com")

    @mock.patch.object(FeedItem, "get_summary")
    @mock.patch.object(FeedItem, "get_body")
    @mock.patch.object(FeedItem, "get_image")
    def test_load_db(self, mock_get_image, mock_get_body, mock_get_summary):
        mock_get_image.return_value = "IMAGE"
        mock_get_body.return_value = "BODY"
        mock_get_summary.return_value = "SUMMARY"
        feed = Feed(feed_id="FEED_ID", url="FEED_URL")
        item = FeedItem({"id": "GUID", "title": "TITLE", "link": "LINK"})
        conn = connect_db(":memory:")
        feed.items = [item]
        feed.load_db(conn)
        row = conn.execute("SELECT * FROM feeds").fetchone()
        self.assertEqual(row["guid"], "GUID")
        self.assertEqual(row["feed_id"], "FEED_ID")
        self.assertEqual(row["title"], "TITLE")
        self.assertEqual(row["body"], "BODY")
        self.assertEqual(row["summary"], "SUMMARY")
        self.assertEqual(row["link"], "LINK")
        self.assertEqual(row["image"], "IMAGE")
        self.assertEqual(row["image_title"], "image")
        self.assertEqual(row["hashtags"], "")
        self.assertEqual(row["posted"], 0)
        self.assertRegex(str(row["timestamp"]), r"[0-9]{10}")


class TestFeedItem(unittest.TestCase):
    @mock.patch.object(FeedItem, "get_tags")
    @mock.patch.object(FeedItem, "get_summary")
    @mock.patch.object(FeedItem, "get_body")
    @mock.patch.object(FeedItem, "get_image")
    def test___init__(
        self, mock_get_image, mock_get_body, mock_get_summary, mock_get_tags
    ):
        mock_get_image.return_value = "IMAGE"
        mock_get_body.return_value = "BODY"
        mock_get_summary.return_value = "SUMMARY"
        item = FeedItem(
            {"id": "ID", "title": "TITLE", "link": "LINK", "tags": ["tag"]},
            category_tags=True,
        )
        self.assertFalse(item.posted)
        self.assertEqual(item.guid, "ID")
        self.assertEqual(item.image, "IMAGE")
        self.assertEqual(item.title, "TITLE")
        self.assertEqual(item.link, "LINK")
        self.assertRegex(str(item.timestamp), r"[0-9]{10}")
        self.assertEqual(item.body, "BODY")
        self.assertEqual(item.summary, "SUMMARY")
        self.assertEqual(item.tags, [])
        mock_get_tags.assert_called_with(["tag"])

    def test_get_id(self):
        self.assertEqual(FeedItem.get_id(FeedItem, {"id": "ID"}), "ID")
        self.assertEqual(FeedItem.get_id(FeedItem, {"link": "LINK"}), hash("LINK"))

    @mock.patch.object(FeedItem, "html2markdown")
    def test_get_body(self, mock_html2markdown):
        mock_html2markdown.return_value = "markdown\n"
        self.assertIsNone(FeedItem.get_body(FeedItem, None))
        body = FeedItem.get_body(FeedItem, ["test"])
        self.assertEqual(body, "markdown")
        mock_html2markdown.assert_called_with("test")

    @mock.patch.object(FeedItem, "get_image_from_summary")
    @mock.patch.object(FeedItem, "get_image_from_summary_detail")
    @mock.patch.object(FeedItem, "get_image_from_content")
    @mock.patch.object(FeedItem, "get_image_from_links")
    @mock.patch.object(FeedItem, "get_image_from_media_thumbnail")
    @mock.patch.object(FeedItem, "get_image_from_media_content")
    def test_get_image(
        self,
        mock_get_image_from_media_content,
        mock_get_image_from_media_thumbnail,
        mock_get_image_from_links,
        mock_get_image_from_content,
        mock_get_image_from_summary_detail,
        mock_get_image_from_summary,
    ):
        mock_get_image_from_media_content.return_value = None
        mock_get_image_from_media_thumbnail.return_value = None
        mock_get_image_from_links.return_value = None
        mock_get_image_from_content.return_value = None
        mock_get_image_from_summary_detail.return_value = None
        mock_get_image_from_summary.return_value = None
        FeedItem.get_image(FeedItem, {})
        mock_get_image_from_media_content.assert_called()
        mock_get_image_from_media_thumbnail.assert_called()
        mock_get_image_from_links.assert_called()
        mock_get_image_from_content.assert_called()
        mock_get_image_from_summary_detail.assert_called()
        mock_get_image_from_summary.assert_called()

    @mock.patch.object(FeedItem, "find_image_link")
    def test_get_image_from_media_content(self, mock_find_image_link):
        mock_find_image_link.return_value = "IMAGE"
        self.assertEqual(
            FeedItem.get_image_from_media_content(FeedItem, [{"url": ""}]), "IMAGE"
        )
        self.assertIsNone(FeedItem.get_image_from_media_content(FeedItem, []))
        self.assertIsNone(FeedItem.get_image_from_media_content(FeedItem, {}))

    @mock.patch.object(FeedItem, "find_image_link")
    def test_get_image_from_media_thumbnail(self, mock_find_image_link):
        mock_find_image_link.return_value = "IMAGE"
        self.assertEqual(
            FeedItem.get_image_from_media_thumbnail(FeedItem, [{"url": ""}]), "IMAGE"
        )
        self.assertIsNone(FeedItem.get_image_from_media_thumbnail(FeedItem, []))
        self.assertIsNone(FeedItem.get_image_from_media_thumbnail(FeedItem, {}))

    def test_get_image_from_links(self):
        self.assertEqual(
            FeedItem.get_image_from_links(
                FeedItem, [{"type": "image/png", "href": "IMAGE"}]
            ),
            "IMAGE",
        )

    @mock.patch.object(FeedItem, "find_image_link")
    def test_get_image_from_content(self, mock_find_image_link):
        mock_find_image_link.return_value = "IMAGE"
        self.assertEqual(
            FeedItem.get_image_from_content(FeedItem, [{"value": ""}]), "IMAGE"
        )
        self.assertIsNone(FeedItem.get_image_from_media_content(FeedItem, []))
        self.assertIsNone(FeedItem.get_image_from_media_content(FeedItem, {}))

    @mock.patch.object(FeedItem, "find_image_link")
    def test_get_image_from_summary_detail(self, mock_find_image_link):
        mock_find_image_link.return_value = "IMAGE"
        self.assertEqual(
            FeedItem.get_image_from_summary_detail(FeedItem, {"value": ""}), "IMAGE"
        )

    @mock.patch.object(FeedItem, "find_image_link")
    def test_get_image_from_summary(self, mock_find_image_link):
        mock_find_image_link.return_value = "IMAGE"
        self.assertEqual(FeedItem.get_image_from_summary(FeedItem, "summary"), "IMAGE")

    def test_find_image_link(self):
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.PNG<-- This is a link",
            ),
            "https://example.com/test.PNG",
        )
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.png<-- This is a link",
            ),
            "https://example.com/test.png",
        )
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.jpg<-- This is a link",
            ),
            "https://example.com/test.jpg",
        )
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.jpeg<-- This is a link",
            ),
            "https://example.com/test.jpeg",
        )
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.tif<-- This is a link",
            ),
            "https://example.com/test.tif",
        )
        self.assertEqual(
            FeedItem.find_image_link(
                FeedItem,
                "This is a link -->https://example.com/test.webp<-- This is a link",
            ),
            "https://example.com/test.webp",
        )
        self.assertIsNone(
            FeedItem.find_image_link(
                FeedItem, "This is a NOT link -->NOT A LINK<-- This is NOT a link"
            )
        )

    @mock.patch.object(FeedItem, "html2markdown")
    def test_get_summary(self, mock_html2markdown):
        FeedItem.get_summary(FeedItem, "summary")
        mock_html2markdown.assert_called_with("summary")

    @mock.patch.object(FeedItem, "add_tags")
    @mock.patch.object(FeedItem, "sanitize_tag")
    def test_get_tags(self, mock_sanitize_tag, mock_add_tags):
        mock_sanitize_tag.return_value = "tag1"
        tags = [{"term": "tag1"}]
        FeedItem.get_tags(FeedItem, tags)
        mock_sanitize_tag.assert_called_with("tag1")
        mock_add_tags.assert_called_with(["tag1"])

    def test_html2markdown(self):
        self.assertEqual(
            FeedItem.html2markdown(
                FeedItem,
                {"type": "text/html", "value": "<strong>Hello world!</strong>"},
            ),
            "**Hello world!**",
        )
        self.assertEqual(
            FeedItem.html2markdown(
                FeedItem, {"type": "text/plain", "value": "Hello world!"}
            ),
            "Hello world!",
        )

    def test_sanitize_tag(self):
        self.assertEqual(FeedItem.sanitize_tag(FeedItem, "Hashtag. "), "#hashtag")

    @mock.patch.object(FeedItem, "get_summary")
    @mock.patch.object(FeedItem, "get_body")
    @mock.patch.object(FeedItem, "get_image")
    @mock.patch.object(FeedItem, "sanitize_tag")
    def test_add_tags(
        self, mock_sanitize_tag, mock_get_body, mock_get_summary, mock_get_tags
    ):
        mock_sanitize_tag.return_value = "#hashtag"
        item = FeedItem({})
        item.add_tags(["hashtag"])
        self.assertEqual(item.tags, ["#hashtag"])

    @mock.patch.object(FeedItem, "get_summary")
    @mock.patch.object(FeedItem, "get_body")
    @mock.patch.object(FeedItem, "get_image")
    @mock.patch.object(FeedItem, "sanitize_tag")
    def test_remove_tags(
        self, mock_sanitize_tag, mock_get_body, mock_get_summary, mock_get_tags
    ):
        mock_sanitize_tag.return_value = "#hashtag"
        item = FeedItem({})
        item.tags = ["#hashtag"]
        item.remove_tags(["hashtag"])
        self.assertEqual(item.tags, [])


class TestPodClient(unittest.TestCase):
    @mock.patch.object(PodClient, "connect")
    @mock.patch("diaspy.connection")
    def test___init__(self, mock_diaspy, mock_connect):
        default = PodClient()
        self.assertIsNone(default.url)
        self.assertIsNone(default.username)
        self.assertIsNone(default.password)
        mock_connect.assert_called()
        custom = PodClient(url="https://example.com", username="user", password="pass")
        self.assertEqual(custom.url, "https://example.com")
        self.assertEqual(custom.username, "user")
        self.assertEqual(custom.password, "pass")

    @mock.patch("diaspy.connection", autospec=True)
    def test_connect(self, mock_diaspy):
        client = PodClient.__new__(PodClient)
        client.url = "https://example.com"
        client.username = "user"
        client.password = "password"
        self.assertIsInstance(client.connect(), diaspy.streams.Stream)
        mock_diaspy.Connection.assert_called()

    @mock.patch("diaspy.streams.Stream")
    @mock.patch("diaspy.connection", autospec=True)
    def test_post(self, mock_diaspy, mock_stream):
        client = PodClient()
        client.post("message")
        client.stream.post.assert_called_with(
            aspect_ids=["public"], provider_display_name=None, text="message"
        )
        client.post("message", aspect_ids=["1"], via="test")
        client.stream.post.assert_called_with(
            aspect_ids=["1"], provider_display_name="test", text="message"
        )

    def test_format_post(self):
        content = {
            "title": "TITLE",
            "link": "LINK",
            "image": "IMAGE",
            "image_title": "IMAGE_TITLE",
            "body": "BODY",
            "summary": "SUMMARY",
            "hashtags": "#hashtag",
        }
        # default
        self.assertRegex(
            PodClient.format_post(PodClient, content),
            r"^### \[TITLE\]\(LINK\)\n\n#hashtag\nposted by \[.*]\(.*\)$",
        )
        # body = True
        self.assertRegex(
            PodClient.format_post(PodClient, content, body=True),
            r"^### \[TITLE\]\(LINK\)\n\nBODY\n\n#hashtag\nposted by \[.*]\(.*\)$",
        )
        # embed_image = True
        self.assertRegex(
            PodClient.format_post(PodClient, content, embed_image=True),
            r"^### \[TITLE\]\(LINK\)\n\n\!\[IMAGE_TITLE\]\(IMAGE\)\n\n#hashtag\nposted by \[.*]\(.*\)$",
        )
        # no_branding = True
        self.assertRegex(
            PodClient.format_post(PodClient, content, no_branding=True),
            r"^### \[TITLE\]\(LINK\)\n\n\#hashtag$",
        )
        # post_raw_link = True
        self.assertRegex(
            PodClient.format_post(PodClient, content, post_raw_link=True),
            r"^### TITLE\n\nLINK\n\n#hashtag\nposted by \[.*]\(.*\)$",
        )
        # summary = True
        self.assertRegex(
            PodClient.format_post(PodClient, content, summary=True),
            r"^### \[TITLE\]\(LINK\)\n\nSUMMARY\n\n#hashtag\nposted by \[.*]\(.*\)$",
        )

    @mock.patch.object(PodClient, "post")
    @mock.patch.object(PodClient, "format_post")
    def test_publish(self, mock_format_post, mock_post):
        class Args:
            def __init__(self):
                self.full = False
                self.summary = "SUMMARY"
                self.no_branding = False
                self.embed_image = False
                self.post_raw_link = False
                self.via = "VIA"
                self.aspect_id = ["public"]

        mock_format_post.return_value = "POST"
        self.assertTrue(PodClient.publish(PodClient, "content", Args()))
        mock_format_post.assert_called_with(
            "content",
            body=False,
            embed_image=False,
            no_branding=False,
            post_raw_link=False,
            summary="SUMMARY",
        )
        mock_post.assert_called_with("POST", aspect_ids=["public"], via="VIA")


class FunctionsTestCase(unittest.TestCase):
    def test_initialize_db(self):
        conn = sqlite3.connect(":memory:")
        initialize_db(conn)
        self.assertEqual(
            conn.execute("PRAGMA table_info('feeds')").fetchall(),
            [
                (0, "guid", "VARCHAR(255)", 0, None, 1),
                (1, "feed_id", "VARCHAR(127)", 0, None, 0),
                (2, "title", "VARCHAR(255)", 0, None, 0),
                (3, "link", "VARCHAR(255)", 0, None, 0),
                (4, "image", "VARCHAR(255)", 0, None, 0),
                (5, "image_title", "VARCHAR(255)", 0, None, 0),
                (6, "hashtags", "VARCHAR(255)", 0, None, 0),
                (7, "timestamp", "INTEGER(10)", 0, None, 0),
                (8, "posted", "INTEGER(1)", 0, None, 0),
                (9, "body", "VARCHAR(10240)", 0, None, 0),
                (10, "summary", "VARCHAR(2048)", 0, None, 0),
            ],
        )

    def test_alter_db(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE feeds(guid VARCHAR(255) PRIMARY KEY)")
        self.assertEqual(
            conn.execute("PRAGMA table_info('feeds')").fetchall(),
            [(0, "guid", "VARCHAR(255)", 0, None, 1)],
        )

    @mock.patch("os.path")
    def test_connect_db(self, mock_path):
        mock_path.isfile.return_value = False
        self.assertIsInstance(connect_db(":memory:"), sqlite3.Connection)

    @mock.patch("pod_feeder_v2.pod_feeder.PodClient")
    def test_publish_items(self, mock_client):
        class Args:
            def __init__(self):
                self.feed_id = "FEED_ID"
                self.limit = 1
                self.timeout = 1
                self.quiet = True

        mock_client.publish.return_value = True
        client = mock_client()
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        initialize_db(conn)
        conn.execute(
            "INSERT INTO feeds(guid, feed_id, title, body, summary, \
            link, image, image_title, hashtags, posted, timestamp) \
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "GUID",
                "FEED_ID",
                "TITLE",
                "BODY",
                "SUMMARY",
                "LINK",
                "IMAGE",
                "image",
                "#hashtag",
                "0",
                time.time(),
            ),
        )
        publish_items(conn, client, Args())
        row = conn.execute(
            "SELECT * FROM feeds WHERE posted = 1 AND guid = 'GUID'"
        ).fetchone()
        self.assertEqual(row["guid"], "GUID")
        client.publish.assert_called()
